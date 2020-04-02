# -*- coding: utf-8 -*-
import re
import pytz
import json
from dateutil import rrule
from datetime import datetime, timedelta, time
from collections import OrderedDict

from django.db.models import Q
from django.views.generic import View, ListView, DetailView
from django.db.models.expressions import RawSQL
from django.db.models import Count, DateTimeField
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.http import HttpResponse

from .models import Alert
from ..agents.models import Agent
from ..locations.models import Location
from ..signatures.models import SignatureCategoryMapping
from ..categories.models import Category


class AlertListView(ListView):
    model = Alert
    template_name = 'alerts/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(AlertListView, self).get_context_data(**kwargs)
        first_alert = Alert.objects.values('timestamp').\
            order_by('timestamp').first()
        last_alert = Alert.objects.values('timestamp').\
            order_by('timestamp').last()
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        start_date = datetime.fromtimestamp(first_alert['timestamp'], tz)
        start_date = datetime.combine(start_date.date(), time())
        end_date = datetime.fromtimestamp(last_alert['timestamp'], tz)
        end_date = datetime.combine(end_date.date(), time()) + \
            timedelta(days=1) - timedelta(seconds=1)
        context['start_date'] = start_date.strftime('%d/%m/%Y %I:%M:%S %p')
        context['end_date'] = end_date.strftime('%d/%m/%Y %I:%M:%S %p')
        return context

    def get_queryset(self):
        return Alert.objects.select_related().all().order_by('-timestamp')


class AlertDetailView(DetailView):
    model = Alert
    template_name = 'alerts/alert_detail.html'
    context_object_name = 'alert'

    def get_object(self):
        return Alert.objects.select_related().get(
            id=self.kwargs.get("alert_id"))


class AlertSearchView(ListView):
    model = Alert
    template_name = 'alerts/alert_search.html'
    context_object_name = 'alerts'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(AlertSearchView, self).get_context_data(**kwargs)
        url_encode = self.request.GET.urlencode(True)
        match = re.match(r'([\&\?]page=(\d)+|page=(\d)+\&)', url_encode)
        if match:
            remove = match.group(0)
            url_encode = url_encode.replace(remove, '')
        context['url_encode'] = url_encode
        return context

    def get_queryset(self):
        daterange = self.request.GET.get('daterange', False)
        categories = self.request.GET.getlist('categories', [])
        users = self.request.GET.getlist('users', [])
        hosts = self.request.GET.getlist('hosts', [])
        levels = self.request.GET.getlist('levels', [])
        # locations = self.request.GET.getlist('locations', [])

        daterange_query = Q()
        # locations_query = Q()
        categories_query = Q()
        users_query = Q()
        hosts_query = Q()
        levels_query = Q()

        if daterange:
            start_date, end_date = daterange.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y %I:%M %p')
            end_date = datetime.strptime(end_date, '%d/%m/%Y %I:%M %p')
            alerts_daterange_ids = Alert.objects.all().\
                annotate(datetime=RawSQL('FROM_UNIXTIME(timestamp)', [],
                         output_field=DateTimeField())).\
                filter(datetime__gte=start_date, datetime__lte=end_date).\
                values_list('id', flat=True)
            daterange_query = Q(id__in=alerts_daterange_ids)

        if categories:
            rule_ids = SignatureCategoryMapping.objects.\
                filter(cat_id__in=categories).values_list(
                    'rule_id', flat=True).distinct()
            categories_query = Q(rule_id__in=rule_ids)

        if hosts:
            filter_agents = Agent.objects.filter(agent_id__in=hosts)
            for agent in filter_agents:
                if agent.agent_id == '000':
                    loca_filter = agent.name.rstrip(' (server)')
                else:
                    loca_filter = agent.ip_address
                location_ids = Location.objects.\
                    filter(name__icontains=loca_filter).\
                    values_list('id', flat=True)
                host_query = Q(location_id__in=list(location_ids))
                hosts_query |= host_query

        # if locations:
        #     locations_query = Q(location_id__in=locations)
        #
        users_query = Q(user__in=users) if users else Q()
        levels_query = Q(level__in=levels) if levels else Q()

        # combine all Q query
        Qquery = Q(daterange_query & hosts_query & categories_query
                   & users_query & levels_query)
        return Alert.objects.select_related().all().filter(Qquery).\
            order_by('-timestamp')


class AlertStatisticsView(View):
    def post(self, request, *args, **kwargs):
        startDate = request.POST.get('startDate', False)
        endDate = request.POST.get('endDate', False)
        result = {}
        if startDate and endDate:
            start_date = datetime.strptime(startDate, '%d/%m/%Y %I:%M %p')
            end_date = datetime.strptime(endDate, '%d/%m/%Y %I:%M %p')
            alert_with_datetime = Alert.objects.all().\
                annotate(datetime=RawSQL('FROM_UNIXTIME(timestamp)', [],
                         output_field=DateTimeField())).\
                filter(datetime__gte=start_date, datetime__lte=end_date)
            diff = end_date - start_date
            if diff.days == 0:
                trunc_alerts = alert_with_datetime.annotate(
                    hour=TruncHour('datetime')).values('hour').\
                    annotate(count=Count('id')).values_list('hour', 'count')
                trunc_alerts = list(trunc_alerts)
                new_trunc_alerts = []
                for dt in rrule.rrule(
                        rrule.HOURLY, dtstart=start_date, until=end_date):
                    new_trunc_alerts.append([dt, 0])

                for new_alert in new_trunc_alerts:
                    for alert in trunc_alerts:
                        if alert[0].replace(tzinfo=None) == new_alert[0]:
                            new_alert[1] = alert[1]

                result['by_time'] = {
                    'label': 'Number of OSSEC alerts in 24 hours',
                    'count': [item[1] for item in new_trunc_alerts],
                    'data':
                        [item[0].strftime("%H") for item in new_trunc_alerts]
                }
            elif diff.days > 0 and diff.days <= 31:
                trunc_alerts = alert_with_datetime.annotate(
                    date=TruncDay('datetime')).values('date').\
                    annotate(count=Count('id')).values_list('date', 'count')
                trunc_alerts = list(trunc_alerts)
                new_trunc_alerts = []
                for dt in rrule.rrule(
                        rrule.DAILY, dtstart=start_date, until=end_date):
                    new_trunc_alerts.append([dt, 0])

                for new_alert in new_trunc_alerts:
                    for alert in trunc_alerts:
                        if alert[0].replace(tzinfo=None) == new_alert[0]:
                            new_alert[1] = alert[1]

                result['by_time'] = {
                    'label': 'Number of OSSEC alerts per days',
                    'count': [item[1] for item in new_trunc_alerts],
                    'data':
                    [item[0].strftime("%d/%m") for item in new_trunc_alerts]
                }
            elif diff.days > 31 and diff.days <= 365:
                trunc_alerts = alert_with_datetime.annotate(
                    date=TruncDay('datetime')).values('date').\
                    annotate(count=Count('id')).values_list('date', 'count')
                trunc_alerts = list(trunc_alerts)
                new_trunc_alerts = OrderedDict()
                for dt in rrule.rrule(
                        rrule.DAILY, dtstart=start_date, until=end_date):
                    isocalendar = dt.isocalendar()
                    week = 'W{0}/{1}'.format(isocalendar[1], isocalendar[0])
                    if week not in new_trunc_alerts:
                        new_trunc_alerts[week] = {
                            'start_date': dt,
                            'count': 0
                        }
                    else:
                        new_trunc_alerts[week]['end_date'] = dt

                for alert in trunc_alerts:
                    isocalendar = alert[0].isocalendar()
                    week = 'W{0}/{1}'.format(isocalendar[1], isocalendar[0])
                    new_trunc_alerts[week]['count'] = \
                        new_trunc_alerts[week]['count'] + alert[1]

                result['by_time'] = {
                    'label': 'Number of OSSEC alerts per weeks',
                    'count':
                    [item['count'] for item in new_trunc_alerts.values()],
                    'data': list(new_trunc_alerts.keys())
                }
            else:
                trunc_alerts = alert_with_datetime.annotate(
                    month=TruncMonth('datetime')).values('month').\
                    annotate(count=Count('id')).values_list('month', 'count')
                trunc_alerts = list(trunc_alerts)
                new_trunc_alerts = []
                for dt in rrule.rrule(
                        rrule.MONTHLY, dtstart=start_date, until=end_date):
                    new_trunc_alerts.append([dt, 0])

                for new_alert in new_trunc_alerts:
                    for alert in trunc_alerts:
                        if alert[0].replace(tzinfo=None) == new_alert[0]:
                            new_alert[1] = alert[1]

                result['by_time'] = {
                    'label': 'Number of OSSEC alerts per months',
                    'count': [item[1] for item in new_trunc_alerts],
                    'data':
                    [item[0].strftime("M%m/%Y") for item in new_trunc_alerts]
                }

            alert_by_cate = alert_with_datetime.select_related('rule').values(
                'rule__rule_id').annotate(count=Count('id')).order_by('-count').\
                values_list('rule__rule_id', 'count')
            # alert_by_cate = alert_by_cate[:10] if alert_by_cate.count() > 10 else \
            #     alert_by_cate

            cate_name_count = {}
            for alert in alert_by_cate:
                cat_ids = SignatureCategoryMapping.objects.filter(
                    rule_id=alert[0]).values_list('cat_id', flat=True)
                categories = Category.objects.filter(cat_id__in=cat_ids)
                for cate in categories:
                    # if len(cate_name_count) > 10:
                    #     break
                    if cate.cat_name not in cate_name_count:
                        cate_name_count[cate.cat_name] = alert[1]
                    else:
                        cate_name_count[cate.cat_name] = \
                            cate_name_count[cate.cat_name] + alert[1]

            by_cate_data = []
            by_cate_count = []
            for key, value in sorted(
                    cate_name_count.items(), key=lambda x: x[1], reverse=True):
                if len(by_cate_data) >= 10:
                    break
                by_cate_data.append(key)
                by_cate_count.append(value)

            result['by_cate'] = {
                'label': 'Top categories of OSSEC alerts',
                'count': by_cate_count,
                'data': by_cate_data,
            }

        return HttpResponse(json.dumps(result))
