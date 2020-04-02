# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.SyscheckListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<syscheck_id>[\w.@+-]+)/$',
        view=views.SyscheckDetailView.as_view(),
        name='detail',
    ),
    url(
        regex=r'^~search/$',
        view=views.SyscheckSearchView.as_view(),
        name='search',
    ),
    url(
        regex=r'^download/([0-9]+)/$',
        view=views.download_syscheck_file,
        name='download',
    ),
    url(
        regex=r'^~statistics/$',
        view=views.SyscheckStatisticsView.as_view(),
        name='statistics'
    ),
]
