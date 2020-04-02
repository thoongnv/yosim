# -*- coding: utf-8 -*-
import json

from ..signatures.models import SignatureCategoryMapping
from ..categories.models import Category
from ..agents.models import Agent
from .models import Alert


def alerts_processor(request):
    context = {}
    allowed_path = ['/alerts/', '/alerts/~search/']

    if request.path in allowed_path:
        # if request.method == 'POST':
        #     # remove critical data
        #     del previous_data['csrfmiddlewaretoken']
        previous_data = {}
        for key, value in request.GET.lists():
            previous_data[key] = ", ".join(value)
        context['previous_data'] = json.dumps(previous_data)

        # get alert hosts
        alert_hosts = Agent.objects.all().values(
            'agent_id', 'name', 'ip_address')

        # get alert levels
        alert_levels = Alert.objects.select_related('level').\
            values('level__number', 'level__common_name').distinct()
        # alert_levels = []
        # for level in levels:
        #     alert_levels.append('{0} - {1}'.format(level[0], level[1]))

        # get alert users
        alert_users = Alert.objects.values_list(
            'user', flat=True).distinct()

        # # get alert locations
        # alert_locations = Alert.objects.select_related('location').\
        #     values_list('location__name', flat=True).distinct()

        # get alert categories
        alert_rule_ids = Alert.objects.select_related('rule').\
            values_list('rule__rule_id', flat=True).distinct()

        alert_cate_ids = SignatureCategoryMapping.objects.filter(
            rule_id__in=alert_rule_ids).values_list(
                'cat_id', flat=True).distinct()

        alert_categories = Category.objects.filter(cat_id__in=alert_cate_ids).\
            values('cat_id', 'cat_name').distinct()

        context['alert_hosts'] = alert_hosts
        context['alert_levels'] = alert_levels
        context['alert_users'] = alert_users
        # context['alert_locations'] = alert_locations
        context['alert_categories'] = alert_categories

        # # get categories
        # categories_lst = Log.objects.distinct('categories').\
        #     values_list('categories', flat=True)
        # categories_names = set()

        # for item in categories_lst:
        #     for category in item:
        #         categories_names.add(category)

        # categories = Category.objects.filter(name__in=categories_names).\
        #     order_by('-priority')

        # # get log_formats
        # location_names = Log.objects.distinct('location').\
        #     select_related('location').values_list(
        #         'location__name', flat=True)

        # format_location_names = set()
        # for location_name in location_names:
        #     format_location = location_name[location_name.index('->') + 2:]
        #     format_location_names.add(format_location)

        # log_formats = LogFormat.objects.filter(
        #     Q(location__in=format_location_names) |
        #     Q(command__in=format_location_names)).distinct('log_format')

    return context
