# -*- coding: utf-8 -*-
import time
import os
import itertools
import xml.etree.ElementTree as ET

from .utilities import get_absolute_path


class LogsCollector(object):
    """Base class for reading file real-time
    """

    def __init__(self, flog, delimiter, alllines=False, realtime=True):
        self.flog = flog
        self.delimiter = delimiter
        self.alllines = alllines
        self.realtime = realtime

    def get_logs_real_time(self):
        try:
            log = []
            flog = open(self.flog, 'r')
        except Exception:
            raise Exception("This script require root privileges to run")

        # read all lines one time
        if self.alllines:
            lines = flog.read()
            yield lines
        else:
            while True:
                line = flog.readline()
                if not line:
                    # flush log incase read a block lines
                    if log:
                        yield log
                        log = []

                    if not self.realtime:
                        break

                    # Sleep briefly
                    time.sleep(0.1)
                    continue

                if not self.delimiter:
                    yield line
                else:
                    if line == self.delimiter:
                        # flush log when save a log completely
                        if log:
                            yield log
                        log = []
                    else:
                        log.append(line)


class XMLCollector(object):
    """Base class for reading XML file
    """

    xml_parses = []

    def __init__(self, xml_path):
        self.xml_path = xml_path

    def get_parsed_xml_files(self):
        if not os.path.isdir(self.xml_path):
            return ET.parse(self.xml_path)
        else:
            for fname in os.listdir(self.xml_path):
                if not fname.startswith("."):
                    fpath = get_absolute_path(self.xml_path, fname)
                    if fpath and os.path.isfile(fpath):
                        with open(fpath) as f:
                            it = itertools.chain('<root>', f, '</root>')
                            root = ET.fromstringlist(it)
                            self.xml_parses.append(root)
            return self.xml_parses
