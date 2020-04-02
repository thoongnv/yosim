# -*- coding: utf-8 -*-
import os
import tailer
import subprocess
from celery import shared_task
from celery.utils.log import get_task_logger

from ..utilities.collector import XMLCollector
from ..utilities.utilities import get_absolute_path, get_default_ossec_params
from ..agents.models import Agent
from ..syschecks.tasks import get_remote_syscheck_connection

logger = get_task_logger(__name__)


def build_syschk_cfg_params(xml_collector):
    config = {}
    xml_parse = xml_collector.get_parsed_xml_files()
    for syscheck in xml_parse.iter('syscheck'):
        tag = syscheck.attrib.get('tag', False)
        if tag and tag not in config:
            config[tag] = {}
        for directory in syscheck.iter('directories'):
            config[tag]['directories'] = directory.text.split(',')
            config[tag]['attributes'] = directory.attrib
    return config


@shared_task(bind=True)
def get_syschk_cfg_params(self):
    params = get_default_ossec_params()
    cfg_fpath = get_absolute_path(params['DIRECTORY'], 'etc/ossec.conf')
    agents = Agent.objects.all()
    syschk_cfg = {}
    for agent in agents:
        if agent.agent_id == '000':
            xml_collector = XMLCollector(cfg_fpath)
            config = build_syschk_cfg_params(xml_collector)
            config['cfg_fpath'] = cfg_fpath
            syschk_cfg.update({
                agent.name: config
            })
        elif 'Active' in agent.agent_status:
            syschk_ssh, syschk_sftp = get_remote_syscheck_connection(
                agent.ip_address)
            local_cfg_fpath = '%s/etc/ossec_%s.conf' % (
                params['DIRECTORY'], agent.agent_id)
            if not syschk_ssh and not syschk_sftp:
                if os.path.isfile(local_cfg_fpath):
                    local_cfg_fpath = '%s/etc/ossec_%s.conf' % (
                        params['DIRECTORY'], agent.agent_id)
                    xml_collector = XMLCollector(local_cfg_fpath)
                    config = build_syschk_cfg_params(xml_collector)
                    config['cfg_fpath'] = local_cfg_fpath
                    syschk_cfg.update({
                        agent.name: config
                    })
            else:
                print('Copy config file: {0} \
                    to OSSEC Server'.format(cfg_fpath))
                syschk_sftp.get(cfg_fpath, local_cfg_fpath)
                xml_collector = XMLCollector(local_cfg_fpath)
                config = build_syschk_cfg_params(xml_collector)
                config['cfg_fpath'] = local_cfg_fpath
                syschk_cfg.update({
                    agent.name: config
                })

    return syschk_cfg


@shared_task(bind=True)
def update_syschk_cfg_params(
        self, syschk_cfg_fpath, user_data_file_dirs, system_cfg_file_dirs):
    new_syschk_cfg = {
        'user_data_file': {
            'directories': user_data_file_dirs.split(',')
        },
        'system_cfg_file': {
            'directories': system_cfg_file_dirs.split(',')
        }
    }
    cfg_fname = os.path.basename(syschk_cfg_fpath)
    is_agent_cfg = True if cfg_fname != 'ossec.conf' else False
    config = False
    is_write_cfg = False
    xml_collector = XMLCollector(syschk_cfg_fpath)
    syschk_config = build_syschk_cfg_params(xml_collector)
    for cfg_type, cfg_data in new_syschk_cfg.items():
        for key, new_value in cfg_data.items():
            if key == 'directories':
                for new_dir in new_value:
                    if not is_agent_cfg:
                        if not os.path.isdir(new_dir):
                            return 'Directory: {} not exists, try again!'.\
                                format(new_dir)
                    else:
                        # TODO check if remote dirs exists
                        pass
                if set(syschk_config[cfg_type][key]) != set(new_value):
                    if not config:
                        config = xml_collector.get_parsed_xml_files()
                    for syscheck in config.iter('syscheck'):
                        tag = syscheck.attrib.get('tag', False)
                        if tag == cfg_type:
                            is_write_cfg = True
                            for directory in syscheck.iter('directories'):
                                directory.text = ','.join(new_value)
    if is_write_cfg:
        config.write(syschk_cfg_fpath)
        if is_agent_cfg:
            apply_ossec_syschk_config.delay(syschk_cfg_fpath)
        else:
            apply_ossec_syschk_config.delay(None)
        return 'Update syscheck configuration successfully, '
        'waiting for OSSEC service restart.'

    return 'No need to update syscheck configuration.'


@shared_task(bind=True)
def apply_ossec_syschk_config(
        self, syschk_cfg_fpath, username='root', key_path='/root/.ssh/id_rsa'):
    if syschk_cfg_fpath:
        ossec_dir, cfg_fname = os.path.split(syschk_cfg_fpath)
        agent_id = cfg_fname[cfg_fname.find('_') + 1: cfg_fname.find('.')]
        agent = Agent.objects.get(agent_id=agent_id)
        if agent and agent.ip_address:
            syschk_ssh, syschk_sftp = get_remote_syscheck_connection(
                agent.ip_address)
            if not syschk_ssh and not syschk_sftp:
                return
            remote_cfg_fpath = '%s/%s' % (ossec_dir, 'ossec.conf')
            print('Update config file: {0} to agent'.format(syschk_cfg_fpath))
            syschk_sftp.put(syschk_cfg_fpath, remote_cfg_fpath)
            stdin, stdout, stderr = syschk_ssh.exec_command(
                '/var/ossec/bin/ossec-control restart')
            for line in stdout:
                print(line.strip('\n'))
    else:
        subprocess.call(['/var/ossec/bin/ossec-control', 'restart'])


@shared_task(bind=True)
def tailer_nline_from_file(self, lines, fname='/var/ossec/logs/ossec.log'):
    return tailer.tail(open(fname), lines)
