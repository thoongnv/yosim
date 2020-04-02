# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^$',
        view=views.SignatureListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^mappings/$',
        view=views.SigCatMappingListView.as_view(),
        name='mapping-list'
    ),
    url(
        regex=r'^(?P<signature_id>[\w.@+-]+)/$',
        view=views.SignatureDetailView.as_view(),
        name='detail'
    ),
    url(
        regex=r'^mappings/(?P<sig_cat_map_id>[\w.@+-]+)/$',
        view=views.SigCatMappingDetailView.as_view(),
        name='mapping-detail'
    )
]
