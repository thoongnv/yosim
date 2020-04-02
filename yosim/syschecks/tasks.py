# -*- coding: utf-8 -*-
import os
import paramiko
import traceback
import hashlib
import magic
from datetime import timedelta
from celery import states
from celery import task, shared_task
from celery.task import periodic_task
from celery.exceptions import Ignore
from collections import OrderedDict

from .models import Syscheck
from ..utilities.collector import LogsCollector
from ..utilities.utilities import (
    get_username_from_uid, get_groupname_from_gid, get_absolute_path,
    get_diff_changes_from_files, get_default_ossec_params,
    count_lines_from_file
)


def get_matching_file_from_hash(diff_queue_dir, md5_hash):
    file_matchs = {}
    for file_name in os.listdir(diff_queue_dir):
        if file_name.startswith('state') or file_name == 'last-entry':
            file_path = get_absolute_path(diff_queue_dir, file_name)
            file_md5_hash = hashlib.md5(
                open(file_path, 'rb').read()).hexdigest()
            if file_md5_hash == md5_hash:
                if file_name == 'last-entry':
                    return file_path
                splits = file_name.split('.')
                timestamp = splits[1] if len(splits) > 1 else '9999999999'
                file_matchs[int(timestamp)] = file_path
    sorted_file_matchs = OrderedDict(
        sorted(file_matchs.items(), key=lambda t: t[0]))
    if len(sorted_file_matchs) == 1:
        return list(sorted_file_matchs.items())[0][1]
    if len(sorted_file_matchs) > 1:
        for item in sorted_file_matchs.items():
            if Syscheck.objects.filter(state_fpath=item[1]).exists():
                continue
            return item[1]
    return None


def get_remote_syscheck_connection(
        hostname, username='root', key_path='/root/.ssh/id_rsa'):
    pkey = paramiko.RSAKey.from_private_key_file(key_path)
    # try to connect
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        print('*** Connecting...')
        client.connect(
            hostname=hostname, username=username, pkey=pkey, timeout=3)
        sftp_client = client.open_sftp()
        return client, sftp_client
    except IOError as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()
        return False, False


def update_local_diff_files(
        syschk_ssh, syschk_sftp, syschk_fpath,
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
                print('Copy file: {0} to OSSEC Server'.format(remote_file))
                syschk_sftp.get(remote_file_path, local_file_path)
    except IOError as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()


def remove_duplicated_syschecks():
    records = Syscheck.objects.all()

    for record in records:
        try:
            Syscheck.objects.get(
                mtime=record.mtime,
                syschk_fpath=record.syschk_fpath,
                fpath=record.fpath)
        except Exception:
            record.delete()


def get_syscheck_info(
        syscheck, syschk_fpath, syschk_diff_dir,
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
        mtime=syschk['mtime'], syschk_fpath=syschk['syschk_fpath'],
        fpath=syschk['fpath'], defaults=syschk)
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
    remove_duplicated_syschecks()


@task(bind=True)
def collect(self, syschk_fpath, syschk_dir, syschk_diff_dir, syschk_delimiter):
    logs = LogsCollector(syschk_fpath, syschk_delimiter, realtime=False)
    syschk_ssh = syschk_sftp = None
    agent_info = {}
    default_syschk_file = '%s/%s' % (syschk_dir, 'syscheck')
    if syschk_fpath != default_syschk_file:
        syschk_fname = os.path.basename(syschk_fpath)
        parts = syschk_fname.split(' ', 2)
        agent_info['name'] = parts[0].strip('()')
        agent_info['ip_address'] = parts[1][0:parts[1].find('->')]
        syschk_ssh, syschk_sftp = get_remote_syscheck_connection(
            str(agent_info['ip_address']))
        if not syschk_ssh and not syschk_sftp:
            self.update_state(
                state=states.FAILURE,
                meta='Can\'t connect to agent: {}'.format(
                    agent_info['ip_address']))
            raise Ignore()

    syschecks = logs.get_logs_real_time()
    curr_syschk_num = 0
    last_syschk_num = Syscheck.objects.filter(
        syschk_fpath=syschk_fpath).count()
    for syscheck in syschecks:
        curr_syschk_num += 1
        if curr_syschk_num <= last_syschk_num:
            continue
        print("\nCollect syscheck from {}: {} - {}".format(
            syschk_fpath, curr_syschk_num, last_syschk_num))
        get_syscheck_info(syscheck, syschk_fpath, syschk_diff_dir,
                          syschk_ssh, syschk_sftp, agent_info)


@periodic_task(run_every=timedelta(seconds=3), bind=True)
def collect_syschecks(self):
    """Script collect syscheck real-time
    """
    params = get_default_ossec_params()
    ossec_dir = params['DIRECTORY']
    syschk_dir = get_absolute_path(ossec_dir, 'queue/syscheck')
    syschk_diff_dir = get_absolute_path(ossec_dir, 'queue/diff/local')
    syschk_delimiter = ''

    # start to check and collect first
    for (dirname, dirs, files) in os.walk(syschk_dir):
        for filename in files:
            if not filename.startswith('.'):
                syschk_fpath = get_absolute_path(syschk_dir, filename)
                line_count = count_lines_from_file(syschk_fpath)
                if line_count > Syscheck.objects.filter(
                        syschk_fpath=syschk_fpath).count():
                    print('Need to collect syscheck from: {}'.
                          format(syschk_fpath))
                    collect.delay(syschk_fpath, syschk_dir,
                                  syschk_diff_dir, syschk_delimiter)

    # wm = pyinotify.WatchManager()       # Watch Manager
    # # events = pyinotify.IN_MODIFY      # watched events
    # events = pyinotify.ALL_EVENTS
    #
    # class EventHandler(pyinotify.ProcessEvent):
    #     def process_IN_MODIFY(self, event):
    #         print("MODIFY event:", event.pathname)
    #         syschk_fpath = event.pathname
    #         collect(syschk_fpath)
    #
    #     def process_IN_ACCESS(self, event):
    #         print("ACCESS event:", event.pathname)
    #
    #     def process_IN_ATTRIB(self, event):
    #         print("ATTRIB event:", event.pathname)
    #
    #     def process_IN_CLOSE_NOWRITE(self, event):
    #         print("CLOSE_NOWRITE event:", event.pathname)
    #
    #     def process_IN_CLOSE_WRITE(self, event):
    #         print("CLOSE_WRITE event:", event.pathname)
    #
    #     def process_IN_CREATE(self, event):
    #         print("CREATE event:", event.pathname)
    #
    #     def process_IN_DELETE(self, event):
    #         print("DELETE event:", event.pathname)
    #
    #     # def process_IN_MODIFY(self, event):
    #     #     print("MODIFY event:", event.pathname)
    #
    #     def process_IN_OPEN(self, event):
    #         print("OPEN event:", event.pathname)
    #
    # handler = EventHandler()
    # notifier = pyinotify.Notifier(wm, handler)
    # wm.add_watch(syschk_dir, events, rec=True)
    # notifier.loop()


@shared_task(bind=True)
def get_syschk_differences(self, syscheck, to_previous=True):
    differences = OrderedDict()
    compare_fields = ['size', 'perms', 'uname', 'gname', 'md5', 'sha1']
    # get similar syschecks
    if to_previous:
        similar_syschks_ids = Syscheck.objects.filter(
            fpath=syscheck.fpath, syschk_fpath=syscheck.syschk_fpath,
            mtime__lte=syscheck.mtime).order_by('-mtime').\
            values_list('id', flat=True)[:2]
        similar_syschecks = Syscheck.objects.filter(
            id__in=sorted(list(similar_syschks_ids)))
    else:
        similar_syschecks = Syscheck.objects.filter(
            fpath=syscheck.fpath, syschk_fpath=syscheck.syschk_fpath).order_by(
                'mtime', '-size')
    for index, syschk in enumerate(similar_syschecks):
        if index == similar_syschecks.count() - 1:  # out of list
            break
        next_syschk = similar_syschecks[index + 1]
        timestamp = next_syschk.mtime
        # get fields change
        differences[timestamp] = OrderedDict()
        if next_syschk.state_fpath:
            differences[timestamp]['syschk_id'] = next_syschk.id
        differences.move_to_end(timestamp)
        for field in compare_fields:
            old_val = getattr(syschk, field, None)
            new_val = getattr(next_syschk, field, None)
            if old_val is not None and new_val \
                    is not None and old_val != new_val:
                differences[timestamp][field] = {
                    'old': old_val, 'new': new_val}
                differences[timestamp].move_to_end(field)
        # get content change
        if syschk.state_fpath and next_syschk.state_fpath:
            differences[timestamp]['git_diff_content'] = \
                get_diff_changes_from_files(
                    syschk.state_fpath, next_syschk.state_fpath)
    return differences


@shared_task(bind=True)
def get_syschk_download(self, file_path):
    download = {}
    if file_path:
        download['content_type'] = magic.from_file(file_path, mime=True)
        with open(file_path, 'rb') as f:
            download['content'] = f.read()
    return download


@shared_task(bind=True)
def get_syschk_content(self, file_path):
    if file_path:
        f = open(file_path, 'r')
        return f.read()
    else:
        return None
