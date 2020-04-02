# -*- coding: utf-8 -*-
from django.apps import AppConfig


class LocationsConfig(AppConfig):
    name = 'yosim.locations'
    verbose_name = "Locations"

    def ready(self):
        pass
