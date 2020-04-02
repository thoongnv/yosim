# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Signature, SignatureCategoryMapping

admin.site.register(Signature)
admin.site.register(SignatureCategoryMapping)
