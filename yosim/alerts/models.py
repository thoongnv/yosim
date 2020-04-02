# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.db.models.signals import post_save
from django.core.signals import request_finished

from django.dispatch import receiver

from ..servers.models import Server
from ..rules.models import Rule, RuleLevel
from ..locations.models import Location


@python_2_unicode_compatible
class Alert(models.Model):
    server = models.ForeignKey(Server)
    rule = models.ForeignKey(Rule, to_field='rule_id', db_index=True)
    level = models.ForeignKey(
        RuleLevel, to_field='number',
        db_index=True, db_column="level", null=True)
    timestamp = models.IntegerField(db_index=True)
    location = models.ForeignKey(Location)
    src_ip = models.CharField(
        "Source IP", max_length=46, db_index=True)
    dst_ip = models.CharField("Destination IP", max_length=46, null=True)
    src_port = models.PositiveIntegerField("Source Port", null=True)
    dst_port = models.PositiveIntegerField("Destination Port", null=True)
    alertid = models.CharField(max_length=30, db_index=True, default=None)
    user = models.CharField(max_length=30)
    full_log = models.TextField()
    is_hidden = models.PositiveSmallIntegerField(default=0)
    tld = models.CharField(max_length=5, db_index=True, default='')

    class Meta:
        db_table = 'alert'

    def __str__(self):
        return "{} - {} - {} - {} - {} - {} - {} - \
                {} - {} - {} - {} - {} - {} - {}".format(
            self.id, self.server, self.rule, self.level,
            self.timestamp, self.location, self.src_ip,
            self.dst_ip, self.src_port, self.dst_port,
            self.alertid, self.user, self.full_log, self.is_hidden,
            self.tld)


@receiver(post_save, sender=Alert)
def my_handler(sender, **kwargs):
    print("\n\nSomething here\n\n")
    print("\n\nSomething here\n\n")
    print("\n\nSomething here\n\n")
    print("\n\nSomething here\n\n")
