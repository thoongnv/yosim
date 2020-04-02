# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.AgentListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<agent_id>[\w.@+-]+)/$',
        view=views.AgentDetailView.as_view(),
        name='detail'
    )
]
