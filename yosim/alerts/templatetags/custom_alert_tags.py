# -*- coding: utf-8 -*-
import json

from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet

from ...agents.models import Agent

register = template.Library()


@register.filter(name="remove_trailing_zeros")
def remove_trailing_zeros(value):
    return str(value).rstrip('0')


@register.filter(name="capitalize_sentence")
def capitalize_sentence(value):
    words = value.split('_')
    words[0] = words[0].capitalize()
    return " ".join(words)


@register.filter(name="jsonify")
def jsonify(value):
    if isinstance(object, QuerySet):
        return serialize('json', object)
    return json.dumps(object)


@register.filter(name="location_convert")
def location_convert(value):
    new_value = value[:value.find('->')]
    agent = Agent.objects.filter(name__icontains=new_value)
    if agent:
        return agent[0].name
    return value[:value.find('->')]
