# -*- coding: utf-8 -*-
import os
import paramiko
import traceback
import hashlib

from django.test import TestCase

from yosim.syschecks.models import Syscheck
from yosim.utilities.collector import LogsCollector
from yosim.utilities.utilities import (
    get_groupname_from_gid, get_username_from_uid,
    get_absolute_path, get_default_ossec_params
)


class TestSyscheck(TestCase):
    def setUp(self):
        params = get_default_ossec_params()
        self.ossec_dir = params['DIRECTORY']
        self.syschk_dir = get_absolute_path(
            self.ossec_dir, 'queue/syscheck')
        self.syschk_diff_dir = get_absolute_path(
            self.ossec_dir, 'queue/diff/local')
        self.syschk_delimiter = ''

    def get_matching_file_from_hash(self, diff_queue_dir, md5_hash):
        for file_name in os.listdir(diff_queue_dir):
            file_path = get_absolute_path(diff_queue_dir, file_name)
            file_md5_hash = hashlib.md5(
                open(file_path, 'rb').read()).hexdigest()
            if file_md5_hash == md5_hash:
                return file_path
        return None

    def get_remote_syscheck_connection(
            self, hostname, username='root', key_path='/root/.ssh/id_rsa'):
        pkey = paramiko.RSAKey.from_private_key_file(key_path)
        # try to connect
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.WarningPolicy())
            print('*** Connecting...')
            try:
                client.connect(
                    hostname=hostname, username=username, pkey=pkey)
                sftp_client = client.open_sftp()
                return client, sftp_client
            except IOError as e:
                print('*** Caught exception: %s: %s' % (e.__class__, e))
                traceback.print_exc()
        except IOError as e:
            print('*** Caught exception: %s: %s' % (e.__class__, e))
            traceback.print_exc()
            try:
                client.close()
            except IOError as e:
                print('*** Caught exception: %s: %s' % (e.__class__, e))
                traceback.print_exc()
        return False

    def update_local_diff_files(
            self, syschk_ssh, syschk_sftp, syschk_fpath,
            local_diff_dir, remote_diff_dir):
        try:
            remote_files = syschk_sftp.listdir(str(remote_diff_dir))
            if remote_files:
                local_dir_path = '%s%s' % (local_diff_dir, syschk_fpath)
                local_dir = get_absolute_path(local_dir_path)
                if not local_dir:
                    # create directory
                    os.makedirs(local_dir_path)
            for remote_file in remote_files:
                # check if file already exists
                local_file_path = '%s%s/%s' % (
                    local_diff_dir, syschk_fpath, remote_file)
                local_file = get_absolute_path(local_file_path)
                if not local_file or remote_file == 'last-entry':
                    # copy file to local
                    remote_file_path = '%s/%s' % (remote_diff_dir, remote_file)
                    syschk_sftp.get(remote_file_path, local_file_path)
        except IOError as e:
            print('*** Caught exception: %s: %s' % (e.__class__, e))
            traceback.print_exc()

    def get_syscheck_info(
            self, syscheck, syschk_fpath, syschk_diff_dir,
            syschk_ssh, syschk_sftp, agent_info):
        syschk = {}
        segments = syscheck.split(':', 5)
        segments = segments[:-1] + segments[-1].split(' ', 2)
        syschk['changes'] = segments[0][:3]
        syschk['size'] = int(segments[0][3:])

        # incase file was deleted
        if len(segments) == 3:
            timestamp = int(segments[1].strip('!'))
            syschk['fpath'] = segments[2].strip('\n')
        else:
            syschk['perms'] = oct(int(segments[1]))[-4:]
            syschk['md5'] = segments[4]
            syschk['sha1'] = segments[5]
            syschk['fpath'] = segments[7].strip('\n')
            timestamp = int(segments[6].strip('!'))
        syschk['mtime'] = timestamp

        if os.path.basename(syschk['fpath']).startswith('.'):
            syschk['is_hidden'] = True

        if len(segments) > 3:
            if not syschk_ssh:
                syschk['uname'] = get_username_from_uid(segments[2])
                syschk['gname'] = get_groupname_from_gid(segments[3])
            else:
                commands = [
                    'getent passwd %s | cut -d: -f1' % segments[2],
                    'getent group %s | cut -d: -f1' % segments[3],
                    'file -i %s | cut -d\; -f2' % syschk['fpath'],
                ]
                stdin, stdout, stderr = syschk_ssh.exec_command(commands[0])
                syschk['uname'] = stdout.read().strip()
                stdin, stdout, stderr = syschk_ssh.exec_command(commands[1])
                syschk['gname'] = stdout.read().strip()

                # retrieve syscheck files from agent
                remote_diff_dir = '%s%s' % (syschk_diff_dir, syschk['fpath'])
                local_diff_dir = '%s%s' % (
                    syschk_diff_dir.strip('local'), agent_info['name'])
                syschk_diff_dir = local_diff_dir
                update_local_diff_files(
                    syschk_ssh, syschk_sftp, syschk['fpath'],
                    local_diff_dir, remote_diff_dir)

            diff_queue_dir = get_absolute_path(
                syschk_diff_dir, syschk['fpath'][1:])
            if diff_queue_dir:
                state_fpath = get_matching_file_from_hash(
                    diff_queue_dir, syschk['md5'])
                syschk['state_fpath'] = state_fpath
                if syschk['state_fpath']:
                    syschk['ftype'] = magic.from_file(
                        syschk['state_fpath'], mime=True)

            syschk['syschk_fpath'] = syschk_fpath

            syscheck, created = Syscheck.objects.get_or_create(
                md5=syschk['md5'], sha1=syschk['sha1'], fpath=syschk['fpath'],
                defaults=syschk)
            if created and syscheck.state_fpath:
                if syschk['state_fpath'].rsplit('/', 1)[1] == 'last-entry':
                    print('Need to update syscheck state_fpath to latest...')
                    update_syschks = Syscheck.objects.filter(
                        syschk_fpath=syscheck.syschk_fpath).exclude(
                            md5=syscheck.md5)
                    for update_syschk in update_syschks:
                        if not update_syschk.state_fpath or \
                                update_syschk.state_fpath == syscheck.state_fpath:
                            new_state_fpath = get_matching_file_from_hash(
                                diff_queue_dir, update_syschk.md5)
                            update_syschk.state_fpath = new_state_fpath
                            update_syschk.save()
                print("New syscheck: {0} at {1}".format(
                    syscheck.fpath, syscheck.mtime))
                syscheck.save()
            else:
                print('Syscheck already exists ...')

    def test_get_syschecks(self):
        for (dirname, dirs, files) in os.walk(self.syschk_dir):
            for filename in files:
                if not filename.startswith('.'):
                    curr_syscheck_num = 0
                    syschk_fpath = get_absolute_path(
                        self.syschk_dir, filename)
                    last_syscheck_num = Syscheck.objects.filter(
                        syschk_fpath=syschk_fpath).count()
                    logs = LogsCollector(
                        # syschk_fpath, self.syschk_delimiter)
                        syschk_fpath, self.syschk_delimiter, realtime=False)
                    syschk_ssh = syschk_sftp = None
                    agent_info = {}
                    if filename != 'syscheck':
                        parts = filename.split(' ')
                        agent_info['name'] = parts[0].strip('()')
                        agent_info['ip_address'] = \
                            parts[1][0:parts[1].find('->')]
                        syschk_ssh, syschk_sftp = \
                            self.get_remote_syscheck_connection(
                                str(agent_info['ip_address']))
                    syschecks = logs.get_logs_real_time()
                    for syscheck in syschecks:
                        curr_syscheck_num += 1
                        if curr_syscheck_num <= last_syscheck_num:
                            continue
                        print("\nCollect syscheck from {}: {} - {}".format(
                            syschk_fpath, curr_syscheck_num,
                            last_syscheck_num))
                        self.get_syscheck_info(
                            syscheck, syschk_fpath, self.syschk_diff_dir,
                            syschk_ssh, syschk_sftp, agent_info)
