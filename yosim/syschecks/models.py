# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ..locations.models import Location
from ..alerts.models import Alert


@python_2_unicode_compatible
class Syscheck(models.Model):
    alert = models.ForeignKey(Alert, blank=True, null=True)
    changes = models.CharField(
        "Changes Counter", max_length=7,
        help_text="Indicate how many times a file was changed")
    size = models.IntegerField("File size (KB)", default=-1)
    perms = models.PositiveIntegerField(
        "File permissions", blank=True, null=True)
    uname = models.CharField(
        "File owner", max_length=15, blank=True, null=True)
    gname = models.CharField(
        "File group-owner", max_length=15, blank=True, null=True)
    md5 = models.CharField("MD5 hash", max_length=32)
    sha1 = models.CharField("SHA1 hash", max_length=40)
    mtime = models.IntegerField("Modified timestamp")
    fpath = models.FilePathField("File path", max_length=200)
    ftype = models.CharField(
        "File type", max_length=100, blank=True, null=True)
    syschk_fpath = models.FilePathField("Syscheck file path", max_length=200)
    location = models.ForeignKey(Location, blank=True, null=True)
    diff_fpath = models.FilePathField(
        "File difference content", max_length=200, blank=True, null=True)
    state_fpath = models.FilePathField(
        "File state content", max_length=200, blank=True, null=True)
    is_hidden = models.BooleanField("Is hidden file", default=False)

    class Meta:
        db_table = 'syscheck'

    def __str__(self):
        return "{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | \
                {} | {} | {} | {} | {}".format(
                self.alert, self.changes, self.size, self.perms,
                self.uname, self.gname, self.md5, self.mtime, self.fpath,
                self.syschk_fpath, self.location, self.diff_fpath,
                self.state_fpath, self.is_hidden, self.ftype)
