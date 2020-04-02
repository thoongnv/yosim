# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Location


class LocationListView(ListView):
    model = Location
    template_name = 'locations/location_list.html'
    context_object_name = 'locations'
    paginate_by = 10

    def get_queryset(self):
        return Location.objects.select_related().all()


class LocationDetailView(DetailView):
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'

    def get_object(self):
        return Location.objects.select_related().get(
            id=self.kwargs.get("location_id"))
