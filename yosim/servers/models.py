# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Server(models.Model):
    last_contact = models.IntegerField()
    version = models.CharField(max_length=32)
    hostname = models.CharField(unique=True, max_length=64)
    information = models.TextField()

    class Meta:
        db_table = 'server'

    def __str__(self):
        return "{} - {} - {} - {}".\
            format(self.last_contact, self.version,
                   self.hostname, self.information)
