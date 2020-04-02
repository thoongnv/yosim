# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.LocationListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<location_id>[\w.@+-]+)/$',
        view=views.LocationDetailView.as_view(),
        name='detail'
    )
]
