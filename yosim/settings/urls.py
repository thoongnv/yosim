# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.SettingsOverview.as_view(),
        name='overview'
    ),
    url(
        regex=r'^~update/$',
        view=views.SettingsUpdate.as_view(),
        name='update'
    )
]
