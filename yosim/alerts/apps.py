# -*- coding: utf-8 -*-
from django.apps import AppConfig


class AlertsConfig(AppConfig):
    name = 'yosim.alerts'
    verbose_name = "Alerts"

    def ready(self):
        pass
