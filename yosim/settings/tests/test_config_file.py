# -*- coding: utf-8 -*-
import os
from django.test import TestCase

from ..tasks import read_ossec_cfg_file


class TestSettings(TestCase):
    def test_read_ossec_cfg_file(self):
        config = read_ossec_cfg_file.delay().get()
        syschk_cfg = {}
        for syscheck in config.iter('syscheck'):
            tag = syscheck.attrib.get('tag', False)
            if tag and tag not in syschk_cfg:
                syschk_cfg[tag] = {}
            for directory in syscheck.iter('directories'):
                syschk_cfg[tag]['directories'] = directory.text.split(',')
                syschk_cfg[tag]['attributes'] = directory.attrib
        print('\n\nconfig', config)
        print('\n\nsyschk_cfg', syschk_cfg)

    def test_write_ossec_cfg_file(self):
        config = read_ossec_cfg_file.delay().get()
        syschk_cfg = {}
        for syscheck in config.iter('syscheck'):
            tag = syscheck.attrib.get('tag', False)
            if tag and tag not in syschk_cfg:
                syschk_cfg[tag] = {}
            for directory in syscheck.iter('directories'):
                syschk_cfg[tag]['directories'] = directory.text.split(',')
                syschk_cfg[tag]['attributes'] = directory.attrib

        new_syschk_cfg = {
            'user_data_file': {
                'directories': ['/home/kuthoong248/Thesis', '/etc/supervisor']
            },
            'system_cfg_file': {
                'directories': ['/etc/supervisor']
            }
        }
        is_write_cfg = False
        for cfg_type, cfg_data in new_syschk_cfg.items():
            for key, new_value in cfg_data.items():
                if key == 'directories':
                    for new_dir in new_value:
                        if not os.path.isdir(new_dir):
                            raise Exception('Directory: {} not exists, \
                        try again!'.format(new_dir))

                    if set(syschk_cfg[cfg_type][key]) != set(new_value):
                        for syscheck in config.iter('syscheck'):
                            tag = syscheck.attrib.get('tag', False)
                            if tag == cfg_type:
                                is_write_cfg = True
                                for directory in syscheck.iter('directories'):
                                    directory.text = ','.join(new_value)
        if is_write_cfg:
            config.write("/home/kuthoong248/projects/yosim/yosim/yosim/settings/tests/ossec2.conf")
