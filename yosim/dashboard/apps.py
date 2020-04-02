# -*- coding: utf-8 -*-
from django.apps import AppConfig


class DashboardConfig(AppConfig):
    name = 'yosim.dashboard'
    verbose_name = "Dashboard"

    def ready(self):
        pass
