# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..rules.models import Rule, RuleLevel
from ..categories.models import Category


@python_2_unicode_compatible
class Signature(models.Model):
    rule = models.ForeignKey(Rule, db_index=True, to_field='rule_id')
    level = models.ForeignKey(
        RuleLevel, db_index=True,
        to_field='number', db_column='level', null=True)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = 'signature'

    def __str__(self):
        return "{} - {} - {}".format(
            self.rule, self.level, self.description)


@python_2_unicode_compatible
class SignatureCategoryMapping(models.Model):
    rule_id = models.PositiveIntegerField()
    cat_id = models.PositiveIntegerField()

    class Meta:
        db_table = 'signature_category_mapping'

    def __str__(self):
        return "{} - {}".format(self.rule_id, self.cat_id)
