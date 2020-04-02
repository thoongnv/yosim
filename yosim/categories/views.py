# -*- coding: utf-8 -*-
from django.views.generic import ListView, DetailView

from .models import Category


class CategoryListView(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'
    paginate_by = 10

    def get_queryset(self):
        return Category.objects.all()


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'categories/category_detail.html'
    context_object_name = 'category'

    def get_object(self):
        return Category.objects.get(cat_id=self.kwargs.get("category_id"))
