# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.AlertListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<alert_id>[\w.@+-]+)/$',
        view=views.AlertDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^~search/$',
        view=views.AlertSearchView.as_view(),
        name='search'
    ),
    url(
        regex=r'^~statistics/$',
        view=views.AlertStatisticsView.as_view(),
        name='statistics'
    ),
]
