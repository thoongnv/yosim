# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from django.db.models.functions import TruncHour, TruncDay
from django.db.models.expressions import RawSQL
from django.db.models import Count, DateTimeField
from django.views.generic.base import TemplateView

from ..alerts.models import Alert
from ..syschecks.models import Syscheck
from ..rules.models import Rule
from ..servers.models import Server
from ..agents.models import Agent
from ..categories.models import Category
from ..signatures.models import SignatureCategoryMapping


class DashboardOverview(TemplateView):
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardOverview, self).get_context_data(**kwargs)
        alerts = Alert.objects.all()
        syschecks = Syscheck.objects.all()
        total_rules = Rule.objects.all().count()
        total_servers = Server.objects.all().count()
        total_agents = Agent.objects.all().count()
        context['total_alerts'] = alerts.count()
        context['total_syschks'] = syschecks.count()
        context['total_rules'] = total_rules
        context['total_servers'] = total_servers
        context['total_agents'] = total_agents
        context['syschecks'] = syschecks.order_by('-mtime')[:5]

        alert_with_datetime = alerts.annotate(datetime=RawSQL(
            'FROM_UNIXTIME(timestamp)', [], output_field=DateTimeField()))

        alert_by_date = alert_with_datetime.annotate(
            date=TruncDay('datetime')).values('date').order_by('-date').\
            annotate(count=Count('id')).values_list('date', 'count')
        alert_by_hour = alert_with_datetime.annotate(
            hour=TruncHour('datetime')).values('hour').order_by('-hour').annotate(
                count=Count('id')).values_list(
                    'hour', 'count')
        alert_by_cate = alerts.select_related('rule').values(
            'rule__rule_id').annotate(count=Count('id')).order_by('-count').\
            values_list('rule__rule_id', 'count')
        alert_by_cate = alert_by_cate[:10] if alert_by_cate.count() > 10 else \
            alert_by_cate

        cate_name_count = {}
        for alert in alert_by_cate:
            cat_ids = SignatureCategoryMapping.objects.filter(
                rule_id=alert[0]).values_list('cat_id', flat=True)
            categories = Category.objects.filter(cat_id__in=cat_ids)
            for cate in categories:
                if len(cate_name_count) > 10:
                    break
                if cate.cat_name not in cate_name_count:
                    cate_name_count[cate.cat_name] = alert[1]

        by_cate = {}
        by_cate['cate'] = []
        by_cate['count'] = []
        for key, value in sorted(
                cate_name_count.items(), key=lambda x: x[1], reverse=True):
            by_cate['cate'].append(key)
            by_cate['count'].append(value)

        # just get some data
        alert_by_date = alert_by_date[:7] \
            if len(alert_by_date) > 7 else alert_by_date
        alert_by_hour = alert_by_hour[:24] \
            if len(alert_by_hour) > 24 else alert_by_hour
        alert_charts = {
            'by_date': {
                'date': [
                    item[0].strftime("%d/%m") for item in alert_by_date],
                'count': [item[1] for item in alert_by_date],
            },
            'by_hour': {
                'hour': [item[0].strftime("%d/%m") for item in alert_by_hour],
                'count': [item[1] for item in alert_by_hour],
            },
            'by_cate': by_cate,
        }

        syschk_by_host = syschecks.values('syschk_fpath').annotate(
            count=Count('id')).values_list('syschk_fpath', 'count')
        syschk_with_datetime = syschecks.annotate(datetime=RawSQL(
            'FROM_UNIXTIME(mtime)', [], output_field=DateTimeField()))

        syschk_by_date = syschk_with_datetime.annotate(
            date=TruncDay('datetime')).values('date').order_by('-date').\
            annotate(count=Count('id')).values_list('date', 'count')

        syschk_cat_id = Category.objects.get(cat_name='syscheck').cat_id
        syschk_rule_ids = SignatureCategoryMapping.objects.filter(
            cat_id=syschk_cat_id).values_list('rule_id', flat=True)
        syschk_alerts = alert_with_datetime.select_related('rule').\
            filter(rule__rule_id__in=syschk_rule_ids)
        syschk_by_type = syschk_alerts.values(
            'rule__decoded_as').annotate(count=Count('rule__decoded_as')).\
            values_list('rule__decoded_as', 'count')

        syschk_types = [item[0] for item in syschk_by_type]
        syschk_alert_dates = syschk_alerts.annotate(
            date=TruncDay('datetime')).distinct().values('date').\
            order_by('-date').values_list('date', flat=True)
        syschk_by_type_date = OrderedDict()
        for date in syschk_alert_dates:
            syschk_type_count = OrderedDict()
            for syschk_type in syschk_types:
                syschk_type_count[syschk_type] = 0
            syschk_type_grp = syschk_alerts.annotate(
                date=TruncDay('datetime')).filter(
                date__date=date, rule__decoded_as__in=syschk_types).values(
                    'rule__decoded_as').annotate(
                count=Count('rule__decoded_as')).values_list(
                    'rule__decoded_as', 'count')
            for syschk_type in syschk_type_grp:
                syschk_type_count[syschk_type[0]] = syschk_type[1]
            syschk_by_type_date[date.strftime("%d/%m")] = syschk_type_count

        chart_datas = []
        for syschk_type in syschk_types:
            chart_dataset = {}
            chart_dataset[syschk_type] = []
            for type_stats in syschk_by_type_date.values():
                chart_dataset[syschk_type].append(type_stats[syschk_type])
            chart_datas.append(chart_dataset)

        # just get some data
        syschk_by_host = syschk_by_host[:10] \
            if len(syschk_by_host) > 10 else syschk_by_host
        syschk_by_date = syschk_by_date[:7] \
            if len(syschk_by_date) > 7 else syschk_by_date

        syschk_charts = {
            'by_host': {
                'host': [item[0] for item in syschk_by_host],
                'count': [item[1] for item in syschk_by_host],
            },
            'by_date': {
                'date': [
                    item[0].strftime("%d/%m") for item in syschk_by_date],
                'count': [item[1] for item in syschk_by_date],
            },
            'by_type': {
                'type': syschk_types,
                'count': [item[1] for item in syschk_by_type],
            },
            'by_type_date': {
                'labels': list(syschk_by_type_date.keys()),
                'datasets': json.dumps(chart_datas),
            },
        }

        context['alert_charts'] = alert_charts
        context['syschk_charts'] = syschk_charts

        return context
