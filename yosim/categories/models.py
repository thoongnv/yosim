# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    cat_id = models.AutoField(primary_key=True)
    cat_name = models.CharField(unique=True, max_length=32)

    class Meta:
        db_table = 'category'

    def __str__(self):
        return "{} - {}".format(self.cat_id, self.cat_name)
