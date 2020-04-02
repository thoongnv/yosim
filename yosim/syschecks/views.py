# -*- coding: utf-8 -*-
import os
import json
import pytz
from dateutil import rrule
from datetime import time, datetime, timedelta
from collections import OrderedDict

from django.views.generic import View, ListView, DetailView
from django.http import HttpResponse, Http404
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.db.models.functions import TruncHour, TruncDay, TruncMonth
from django.db.models import DateTimeField

from .models import Syscheck
from .tasks import (
    get_syschk_differences, get_syschk_download, get_syschk_content)
from ..settings.tasks import get_syschk_cfg_params
from ..agents.models import Agent


class SyscheckListView(ListView):
    model = Syscheck
    template_name = 'syschecks/syscheck_list.html'
    context_object_name = 'syschecks'

    def get_context_data(self, **kwargs):
        context = super(SyscheckListView, self).get_context_data(**kwargs)
        first_syschk = Syscheck.objects.values('mtime').\
            order_by('mtime').first()
        last_syschk = Syscheck.objects.values('mtime').order_by('mtime').last()
        tz = pytz.timezone('Asia/Ho_Chi_Minh')
        start_date = datetime.fromtimestamp(first_syschk['mtime'], tz)
        start_date = datetime.combine(start_date.date(), time())
        end_date = datetime.fromtimestamp(last_syschk['mtime'], tz)
        end_date = datetime.combine(end_date.date(), time()) + \
            timedelta(days=1) - timedelta(seconds=1)
        context['start_date'] = start_date.strftime('%d/%m/%Y %I:%M:%S %p')
        context['end_date'] = end_date.strftime('%d/%m/%Y %I:%M:%S %p')
        return context

    def get_queryset(self):
        return Syscheck.objects.select_related().all().order_by('-mtime')


class SyscheckDetailView(DetailView):
    model = Syscheck
    template_name = 'syschecks/syscheck_detail.html'
    context_object_name = 'syscheck'
    pk_url_kwarg = 'syscheck_id'

    def get_context_data(self, **kwargs):
        context = super(SyscheckDetailView, self).get_context_data(**kwargs)
        syscheck = Syscheck.objects.get(id=self.kwargs.get("syscheck_id"))
        context['syscheck'] = syscheck
        if syscheck.ftype == 'text/plain':
            context['curr_content'] = get_syschk_content.delay(
                syscheck.state_fpath).get(timeout=3)
        context['previous_diffs'] = get_syschk_differences.\
            delay(syscheck).get(timeout=3)
        context['all_diffs'] = get_syschk_differences.\
            delay(syscheck, False).get(timeout=3)
        return context


class SyscheckSearchView(ListView):
    model = Syscheck
    template_name = 'syschecks/syscheck_search.html'
    context_object_name = 'syschecks'

    def get_queryset(self):
        daterange = self.request.GET.get('daterange', False)
        owners = self.request.GET.getlist('owners', [])
        hosts = self.request.GET.getlist('hosts', [])
        ftypes = self.request.GET.getlist('ftypes', [])
        fpatterns = self.request.GET.get('fpatterns', False)
        hosts_query = Q()
        daterange_query = Q()
        ftypes_query = Q()

        if daterange:
            start_date, end_date = daterange.split(' - ')
            start_date = datetime.strptime(start_date, '%d/%m/%Y %I:%M %p')
            end_date = datetime.strptime(end_date, '%d/%m/%Y %I:%M %p')
            syschks_daterange_ids = Syscheck.objects.all().\
                annotate(datetime=RawSQL('FROM_UNIXTIME(mtime)', [],
                         output_field=DateTimeField())).\
                annotate(date=TruncDay('datetime')).values('date').\
                filter(date__gte=start_date, date__lte=end_date).\
                values_list('id', flat=True)
            daterange_query = Q(id__in=syschks_daterange_ids)

        if hosts:
            syschk_fpath = []
            syschk_dir = '/var/ossec/queue/syscheck'
            for host in hosts:
                if '127.0.0.1' in host:
                    fpath = '%s/%s' % (syschk_dir, 'syscheck')
                else:
                    fpath = '%s/%s%s' % (syschk_dir, host, '->syscheck')
                syschk_fpath.append(fpath)
            hosts_query = Q(syschk_fpath__in=syschk_fpath)

        if ftypes and len(ftypes) < 2:
            syschk_cfg = get_syschk_cfg_params.delay().get()
            dirs = []
            for syschk in syschk_cfg.values():
                for key, value in syschk.items():
                    if key == ftypes[0]:
                        directories = value.get('directories', False)
                        if directories:
                            for directory in directories:
                                dirs.append(directory)
            for directory in dirs:
                ftype_query = Q(fpath__startswith='{0}/'.format(directory))
                ftypes_query |= ftype_query

        owners_query = Q(uname__in=owners) if owners else Q()
        fpatterns_query = Q(fpath__icontains=fpatterns) if fpatterns else Q()

        # combine all Q query
        Qquery = Q(daterange_query & owners_query & hosts_query &
                   fpatterns_query & ftypes_query)
        return Syscheck.objects.select_related().all().filter(Qquery).\
            order_by('-mtime')


class SyscheckStatisticsView(View):
    def post(self, request, *args, **kwargs):
        startDate = request.POST.get('startDate', False)
        endDate = request.POST.get('endDate', False)
        result = {}
        if startDate and endDate:
            start_date = datetime.strptime(startDate, '%d/%m/%Y %I:%M %p')
            end_date = datetime.strptime(endDate, '%d/%m/%Y %I:%M %p')
            syschecks = Syscheck.objects.all()
            syschk_hosts = syschecks.values('syschk_fpath').distinct().\
                values_list('syschk_fpath', flat=True)
            syschk_with_datetime = syschecks.\
                annotate(datetime=RawSQL('FROM_UNIXTIME(mtime)', [],
                         output_field=DateTimeField())).\
                filter(datetime__gte=start_date, datetime__lte=end_date)

            diff = end_date - start_date
            datasets = {}
            if diff.days == 0:
                trunc_syschks = syschk_with_datetime.annotate(
                    hour=TruncHour('datetime'))

                syschk_times = []
                for dt in rrule.rrule(
                        rrule.HOURLY, dtstart=start_date, until=end_date):
                    syschk_times.append(dt)

                datasets['text'] = 'Number of syscheck in 24 hours per hosts'
                datasets['datas'] = OrderedDict()
                datasets['labels'] = []
                for syschk_time in syschk_times:
                    datasets['labels'].append(syschk_time.strftime("%H"))
                    for syschk_host in syschk_hosts:
                        if syschk_host not in datasets['datas']:
                            datasets['datas'][syschk_host] = []
                        trunc_syschks_count = trunc_syschks.\
                            filter(syschk_fpath=syschk_host,
                                   hour=pytz.utc.localize(syschk_time)).count()
                        datasets['datas'][syschk_host].\
                            append(trunc_syschks_count)
                result['by_time_host'] = datasets
            elif diff.days > 0 and diff.days <= 31:
                trunc_syschks = syschk_with_datetime.annotate(
                    date=TruncDay('datetime'))

                syschk_times = []
                for dt in rrule.rrule(
                        rrule.DAILY, dtstart=start_date, until=end_date):
                    syschk_times.append(dt)

                datasets['text'] = 'Number of syschecks per days each host'
                datasets['datas'] = OrderedDict()
                datasets['labels'] = []
                for syschk_time in syschk_times:
                    datasets['labels'].append(syschk_time.strftime("%d/%m"))
                    for syschk_host in syschk_hosts:
                        if syschk_host not in datasets['datas']:
                            datasets['datas'][syschk_host] = []
                        trunc_syschks_count = trunc_syschks.\
                            filter(syschk_fpath=syschk_host,
                                   date=pytz.utc.localize(syschk_time)).count()
                        datasets['datas'][syschk_host].\
                            append(trunc_syschks_count)
                result['by_time_host'] = datasets
            elif diff.days > 31 and diff.days <= 365:
                trunc_syschks = syschk_with_datetime.annotate(
                    hour=TruncHour('datetime'))

                syschk_times = OrderedDict()
                for dt in rrule.rrule(
                        rrule.DAILY, dtstart=start_date, until=end_date):
                    isocalendar = dt.isocalendar()
                    week = 'W{0}/{1}'.format(isocalendar[1], isocalendar[0])
                    if week not in syschk_times:
                        syschk_times[week] = {}
                        syschk_times[week]['start_date'] = dt
                    else:
                        syschk_times[week]['end_date'] = dt

                datasets['text'] = 'Number of syschecks per weeks each host'
                datasets['datas'] = OrderedDict()
                datasets['labels'] = []
                for week, week_dates in syschk_times.items():
                    datasets['labels'].append(week)
                    for syschk_host in syschk_hosts:
                        if syschk_host not in datasets['datas']:
                            datasets['datas'][syschk_host] = []
                        trunc_syschks_count = trunc_syschks.\
                            filter(syschk_fpath=syschk_host,
                                   datetime__gte=week_dates['start_date'],
                                   datetime__lte=week_dates['end_date']).\
                            count()
                        datasets['datas'][syschk_host].\
                            append(trunc_syschks_count)
                result['by_time_host'] = datasets
            else:
                trunc_syschks = syschk_with_datetime.annotate(
                    month=TruncMonth('datetime'))

                syschk_times = []
                for dt in rrule.rrule(
                        rrule.MONTHLY, dtstart=start_date, until=end_date):
                    syschk_times.append(dt)

                datasets['text'] = 'Number of syschecks per months each host'
                datasets['datas'] = OrderedDict()
                datasets['labels'] = []
                for syschk_time in syschk_times:
                    datasets['labels'].append(syschk_time.strftime("M%m/%Y"))
                    for syschk_host in syschk_hosts:
                        if syschk_host not in datasets['datas']:
                            datasets['datas'][syschk_host] = []
                        trunc_syschks_count = trunc_syschks.\
                            filter(syschk_fpath=syschk_host,
                                   month=pytz.utc.localize(syschk_time)).count()
                        datasets['datas'][syschk_host].\
                            append(trunc_syschks_count)
                result['by_time_host'] = datasets

            datasets_new_datas = OrderedDict()
            for key in datasets['datas'].keys():
                fname = os.path.basename(key)
                if fname == 'syscheck':
                    agent = Agent.objects.get(agent_id='000')
                    new_host_name = agent.name
                else:
                    new_host_name = fname[:fname.find('->')]
                datasets_new_datas[str(new_host_name)] = \
                    datasets['datas'][key]
            datasets['datas'] = datasets_new_datas

            by_host_data = []
            by_host_count = []
            for syschk_host in syschk_hosts:
                by_host_count.append(
                    syschk_with_datetime.
                    filter(syschk_fpath=syschk_host).count())

                fname = os.path.basename(syschk_host)
                if fname == 'syscheck':
                    agent = Agent.objects.get(agent_id='000')
                    new_host_name = agent.name
                else:
                    new_host_name = fname[:fname.find('->')]
                by_host_data.append(new_host_name)

            result['by_host'] = {
                'label': 'Number of syschecks per hosts',
                'count': by_host_count,
                'data': by_host_data,
            }

        return HttpResponse(json.dumps(result))


def download_syscheck_file(request, syschk_id):
    syscheck = Syscheck.objects.get(pk=syschk_id)
    download = get_syschk_download.delay(syscheck.state_fpath).get(timeout=3)
    if download:
        response = HttpResponse(
            download['content'], content_type=syscheck.ftype)
        response['Content-Disposition'] = 'attachment; filename={}'.\
            format(os.path.basename(syscheck.fpath))
        return response
    raise Http404
