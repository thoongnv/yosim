# -*- coding: utf-8 -*-
import os
import platform
import json

from ..syschecks.models import Syscheck


def syschecks_processor(request):
    context = {}
    allowed_path = ['/syschecks/', '/syschecks/~search/']

    if request.path in allowed_path:
        # if request.method == 'POST':
        #     # remove critical data
        #     del previous_data['csrfmiddlewaretoken']
        previous_data = {}
        for key, value in request.GET.lists():
            previous_data[key] = ", ".join(value)
        context['previous_data'] = json.dumps(previous_data)

        # get syscheck owners
        syschk_owners = Syscheck.objects.values_list(
            'uname', flat=True).distinct()

        # get syscheck hosts
        syschk_fpath = Syscheck.objects.values_list(
            'syschk_fpath', flat=True).distinct()
        syschk_hosts = []
        for fpath in syschk_fpath:
            fname = os.path.basename(fpath)
            if fname == 'syscheck':
                host = '(' + platform.node() + ') 127.0.0.1'
            else:
                host = fname[:fname.find('->syscheck')]
            syschk_hosts.append(host)

        syschk_ftypes = {
            'user_data_file': 'User Data File',
            'system_cfg_file': 'System Configuration File',
        }

        context['syschk_hosts'] = syschk_hosts
        context['syschk_owners'] = syschk_owners
        context['syschk_ftypes'] = syschk_ftypes

    return context
