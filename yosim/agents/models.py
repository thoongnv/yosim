# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..servers.models import Server


@python_2_unicode_compatible
class Agent(models.Model):
    name = models.CharField(max_length=64)
    agent_id = models.CharField(max_length=10)
    agent_status = models.CharField(max_length=20)
    ip_address = models.CharField(max_length=46)
    server = models.ForeignKey(Server)
    last_contact = models.IntegerField(null=True)
    version = models.CharField(max_length=32)
    information = models.CharField(max_length=128)

    class Meta:
        db_table = 'agent'

    def __str__(self):
        return "{} - {} - {} - {} - {} - {} - {} - {} - {}".\
            format(self.id, self.name, self.agent_id, self.agent_status,
                   self.ip_address, self.server, self.last_contact,
                   self.version, self.information)
