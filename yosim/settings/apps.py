# -*- coding: utf-8 -*-
from django.apps import AppConfig


class SettingsConfig(AppConfig):
    name = 'yosim.settings'
    verbose_name = "Settings"

    def ready(self):
        pass
