# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class RuleLevel(models.Model):
    number = models.PositiveIntegerField("Rule level", primary_key=True)
    common_name = models.CharField("Short name", max_length=100, default='')
    description = models.TextField("Description", default='')

    class Meta:
        db_table = 'rule_level'

    def __str__(self):
        return "{} - {} - {}".format(self.number, self.common_name,
                                     self.description)


@python_2_unicode_compatible
class Rule(models.Model):
    level = models.ForeignKey(RuleLevel, to_field='number', db_column='level')
    rule_id = models.PositiveIntegerField(unique=True, default=0)
    maxsize = models.PositiveIntegerField(default=0)
    frequency = models.PositiveIntegerField(default=0)
    timeframe = models.PositiveIntegerField(default=0)
    noalert = models.PositiveIntegerField(default=0)
    ignore_attr = models.PositiveIntegerField(default=0)
    overwrite = models.CharField(max_length=10, default='')
    match = models.CharField(max_length=300, default='')
    regex = models.CharField(max_length=300, default='')
    ignore = models.CharField(max_length=45, default='')
    decoded_as = models.CharField(max_length=45, default='')
    category = models.CharField(max_length=45, default='')
    srcip = models.CharField(max_length=45, default='')
    dstip = models.CharField(max_length=45, default='')
    extra_data = models.CharField(max_length=200, default='')
    user = models.CharField(max_length=300, default='')
    program_name = models.CharField(max_length=30, default='')
    hostname = models.CharField(max_length=30, default='')
    time = models.CharField(max_length=30, default='')
    weekday = models.CharField(max_length=30, default='')
    regex_id = models.CharField(max_length=300, default='')
    url = models.TextField(default='')
    if_sid = models.CharField(max_length=30, default='')
    if_group = models.CharField(max_length=30, default='')
    if_level = models.PositiveIntegerField(default=0)
    if_matched_sid = models.CharField(max_length=30, default='')
    if_matched_group = models.CharField(max_length=30, default='')
    same_id = models.CharField(max_length=10, default='')
    same_source_ip = models.CharField(max_length=10, default='')
    same_source_port = models.CharField(max_length=10, default='')
    same_dst_port = models.CharField(max_length=10, default='')
    same_location = models.CharField(max_length=10, default='')
    same_user = models.CharField(max_length=10, default='')
    description = models.CharField(max_length=200, default='')
    rule_list = models.CharField(max_length=100, default='')
    info = models.CharField(max_length=300, default='')
    options = models.CharField(max_length=200, default='')
    check_diff = models.CharField(max_length=10, default='')
    group = models.CharField(max_length=45, default='')
    action = models.CharField(max_length=30, default='')
    status = models.CharField(max_length=100, default='')
    if_fts = models.CharField(max_length=10, default='')
    check_if_ignored = models.CharField(max_length=10, default='')
    compiled_rule = models.CharField(max_length=30, default='')
    different_url = models.CharField(max_length=10, default='')
    unknown = models.CharField(max_length=500, default='')

    class Meta:
        db_table = 'rule'

    def __str__(self):
        return "{} - {} - {} - {} - {} - {} - {} - {} - {} - {} - \
        {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - \
        {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - \
        {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {} - {}".\
            format(self.level, self.rule_id, self.maxsize, self.frequency,
                   self.timeframe, self.noalert, self.ignore_attr,
                   self.overwrite, self.match, self.regex, self.ignore,
                   self.decoded_as, self.category, self.srcip, self.dstip,
                   self.extra_data, self.user, self.program_name,
                   self.hostname, self.time, self.weekday, self.regex_id,
                   self.url, self.if_sid, self.if_group, self.if_level,
                   self.if_matched_sid, self.if_matched_group, self.same_id,
                   self.same_source_ip, self.same_source_port,
                   self.same_dst_port, self.same_location, self.same_user,
                   self.description, self.rule_list, self.info, self.options,
                   self.check_diff, self.group, self.action, self.status,
                   self.if_fts, self.check_if_ignored, self.compiled_rule,
                   self.different_url, self.unknown)
