# -*- coding: utf-8 -*-
from django.apps import AppConfig


class RulesConfig(AppConfig):
    name = 'yosim.rules'
    verbose_name = "Rules"

    def ready(self):
        pass
