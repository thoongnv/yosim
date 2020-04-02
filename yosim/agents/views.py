# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Agent


class AgentListView(ListView):
    model = Agent
    template_name = 'agents/agent_list.html'
    context_object_name = 'agents'

    def get_queryset(self):
        return Agent.objects.select_related().all()


class AgentDetailView(DetailView):
    model = Agent
    template_name = 'agents/agent_detail.html'
    context_object_name = 'agent'

    def get_object(self):
        return Agent.objects.select_related().get(
            id=self.kwargs.get("agent_id"))
