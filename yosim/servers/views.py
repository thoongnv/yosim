# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Server


class ServerListView(ListView):
    model = Server
    template_name = 'servers/server_list.html'
    context_object_name = 'servers'
    paginate_by = 10

    def get_queryset(self):
        return Server.objects.all()


class ServerDetailView(DetailView):
    model = Server
    template_name = 'servers/server_detail.html'
    context_object_name = 'server'

    def get_object(self):
        return Server.objects.get(id=self.kwargs.get("server_id"))
