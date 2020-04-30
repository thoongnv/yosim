# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-25 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('servers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='servers.Server')),
            ],
            options={
                'db_table': 'location',
            },
        ),
    ]