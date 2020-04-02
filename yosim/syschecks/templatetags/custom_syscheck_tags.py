# -*- coding: utf-8 -*-
import pytz
import platform
from datetime import datetime

from django import template


register = template.Library()

PERMISSIONS = {
    0: 'None',
    1: 'Execute Only',
    2: 'Write Only',
    3: 'Write & Execute',
    4: 'Read Only',
    5: 'Read & Execute',
    6: 'Read & Write',
    7: 'Full Access'
}


@register.filter(name="timestamp_convert")
def timestamp_convert(timestamp):
    try:
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        return datetime.fromtimestamp(timestamp, tz).\
            strftime('%d/%m/%Y %H:%M:%S %p')
    except Exception as e:
        print(e)


@register.filter(name="to_syscheck_node")
def to_syscheck_node(value):
    if value == '/var/ossec/queue/syscheck/syscheck':
        new_value = '(' + platform.node() + ') 127.0.0.1'
    else:
        new_value = value[value.find('('):value.find('->syscheck')]

    return new_value


@register.filter(name="to_readable_permissions")
def to_readable_permissions(value):
    filemode = str(value)
    new_value = '{} | Owner({}) - Group({}) - Other({})'.format(
        filemode, PERMISSIONS.get(int(filemode[-3])),
        PERMISSIONS.get(int(filemode[-2])),
        PERMISSIONS.get(int(filemode[-1]))
    )

    return new_value
