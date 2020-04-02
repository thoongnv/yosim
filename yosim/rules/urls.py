# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.RuleListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<alert_id>[\w.@+-]+)/$',
        view=views.RuleDetailView.as_view(),
        name='detail'
    )
]
