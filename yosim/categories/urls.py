# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.CategoryListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^(?P<category_id>[\w.@+-]+)/$',
        view=views.CategoryDetailView.as_view(),
        name='detail'
    )
]
