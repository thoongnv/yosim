# -*- coding: utf-8 -*-
import os
import grp
import pwd
import subprocess


def get_default_ossec_params():
    res = {}
    conf_file = '/etc/ossec-init.conf'
    try:
        f = open(conf_file, 'r')
        lines = f.readlines()
        for line in lines:
            key, value = line.strip().split('=')
            res[key] = value.strip('"')
        return res
    except Exception as e:
        raise e


def get_regex_result(regex_compiled, source, num_grp=0, is_matchall=False):
    if is_matchall:
        match = regex_compiled.findall(source)
        result = match[num_grp] if match[num_grp] is not None else ''
    else:
        match = regex_compiled.search(source)
        result = match.group(num_grp) if match is not None else ''
    strip_chars = ".:,-'\ "
    return result.strip(strip_chars)


def get_diff_changes_from_files(first_fpath, second_fpath):
    process = subprocess.Popen(
        ['sudo', 'git', 'diff', first_fpath, second_fpath],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    git_diff = process.stdout.read()
    if git_diff:
        return git_diff.decode("utf-8").\
            encode("utf-8").decode("utf-8")
    return None


def get_file_content(filepath):
    try:
        if os.stat(filepath).st_size == 0:
            return None
        else:
            with open(filepath) as f:
                lines = f.readline()
                return lines
    except Exception:
        return None


def get_username_from_uid(uid):
    try:
        username = pwd.getpwuid(int(uid))[0]
    except Exception:
        username = uid
    return username


def get_groupname_from_gid(gid):
    try:
        groupname = grp.getgrgid(int(gid))[0]
    except Exception:
        groupname = gid
    return groupname


def get_absolute_path(file_dir, file_name=None):
    if file_name:
        absolute_path = os.path.abspath(os.path.join(file_dir, file_name))
    else:
        absolute_path = file_dir
    if os.path.isfile(absolute_path) or os.path.isdir(absolute_path):
        return absolute_path
    return None


def count_lines_from_file(filepath):
    return int(subprocess.check_output(
        'wc -l "{}"'.format(filepath), shell=True).split()[0])
