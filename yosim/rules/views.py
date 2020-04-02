# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Rule


class RuleListView(ListView):
    model = Rule
    template_name = 'rules/rule_list.html'
    context_object_name = 'rules'
    paginate_by = 10

    def get_queryset(self):
        return Rule.objects.all().order_by('rule_id')


class RuleDetailView(DetailView):
    model = Rule
    template_name = 'rules/rule_detail.html'
    context_object_name = 'rule'

    def get_object(self):
        return Rule.objects.get(id=self.kwargs.get("rule_id"))
