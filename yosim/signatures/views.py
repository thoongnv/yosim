# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Signature, SignatureCategoryMapping


class SignatureListView(ListView):
    model = Signature
    template_name = 'signatures/signature_list.html'
    context_object_name = 'signatures'
    paginate_by = 10

    def get_queryset(self):
        return Signature.objects.select_related().all()


class SignatureDetailView(DetailView):
    model = SignatureCategoryMapping
    template_name = 'signatures/signature_detail.html'
    context_object_name = 'signature'

    def get_object(self):
        return Signature.objects.select_related().get(
            id=self.kwargs.get("signature_id"))


class SigCatMappingListView(ListView):
    model = SignatureCategoryMapping
    template_name = 'signatures/sig_cat_mapping_list.html'
    context_object_name = 'sig_cat_mappings'
    paginate_by = 10

    def get_queryset(self):
        return SignatureCategoryMapping.objects.select_related().all()


class SigCatMappingDetailView(DetailView):
    model = SignatureCategoryMapping
    template_name = 'signatures/sig_cat_mapping_detail.html'
    context_object_name = 'sig_cat_mapping'

    def get_object(self):
        return SignatureCategoryMapping.objects.select_related().get(
            id=self.kwargs.get("sig_cat_map_id"))
