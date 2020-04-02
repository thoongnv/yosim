# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..servers.models import Server


@python_2_unicode_compatible
class Location(models.Model):
    server = models.ForeignKey(Server)
    name = models.CharField(max_length=128)

    class Meta:
        db_table = 'location'

    def __str__(self):
        return "{} - {}".format(self.server, self.name)
