# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.ServerListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<server_id>[\w.@+-]+)/$',
        view=views.ServerDetailView.as_view(),
        name='detail'
    )
]
