# -*- coding: utf-8 -*-
from django.apps import AppConfig


class SyscheckConfig(AppConfig):
    name = 'yosim.syschecks'
    verbose_name = 'Syscheck'

    def ready(self):
        pass
