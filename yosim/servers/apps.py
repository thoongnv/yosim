# -*- coding: utf-8 -*-
from django.apps import AppConfig


class ServersConfig(AppConfig):
    name = 'yosim.servers'
    verbose_name = "Servers"

    def ready(self):
        pass
