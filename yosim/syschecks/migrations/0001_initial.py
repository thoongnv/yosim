# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-12-25 16:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('alerts', '__first__'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Syscheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('changes', models.CharField(help_text='Indicate how many times a file was changed', max_length=7, verbose_name='Changes Counter')),
                ('size', models.IntegerField(default=-1, verbose_name='File size (KB)')),
                ('perms', models.PositiveIntegerField(blank=True, null=True, verbose_name='File permissions')),
                ('uname', models.CharField(blank=True, max_length=15, null=True, verbose_name='File owner')),
                ('gname', models.CharField(blank=True, max_length=15, null=True, verbose_name='File group-owner')),
                ('md5', models.CharField(max_length=32, verbose_name='MD5 hash')),
                ('sha1', models.CharField(max_length=40, verbose_name='SHA1 hash')),
                ('mtime', models.IntegerField(verbose_name='Modified timestamp')),
                ('fpath', models.FilePathField(max_length=200, verbose_name='File path')),
                ('ftype', models.CharField(blank=True, max_length=100, null=True, verbose_name='File type')),
                ('syschk_fpath', models.FilePathField(max_length=200, verbose_name='Syscheck file path')),
                ('diff_fpath', models.FilePathField(blank=True, max_length=200, null=True, verbose_name='File difference content')),
                ('state_fpath', models.FilePathField(blank=True, max_length=200, null=True, verbose_name='File state content')),
                ('is_hidden', models.BooleanField(default=False, verbose_name='Is hidden file')),
                ('alert', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='alerts.Alert')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='locations.Location')),
            ],
            options={
                'db_table': 'syscheck',
            },
        ),
    ]
