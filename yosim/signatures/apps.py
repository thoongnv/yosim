# -*- coding: utf-8 -*-
from django.apps import AppConfig


class SignaturesConfig(AppConfig):
    name = 'yosim.signatures'
    verbose_name = "Signatures"

    def ready(self):
        pass
