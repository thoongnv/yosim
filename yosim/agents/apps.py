# -*- coding: utf-8 -*-
from django.apps import AppConfig


class AgentsConfig(AppConfig):
    name = 'yosim.agents'
    verbose_name = "Agents"

    def ready(self):
        pass
