# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-25 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('cat_id', models.AutoField(primary_key=True, serialize=False)),
                ('cat_name', models.CharField(max_length=32, unique=True)),
            ],
            options={
                'db_table': 'category',
            },
        ),
    ]
