# -*- coding: utf-8 -*-
from django.views.generic.base import TemplateView, RedirectView
from django.urls import reverse_lazy

from .tasks import (
    get_syschk_cfg_params, update_syschk_cfg_params, tailer_nline_from_file
)


class SettingsOverview(TemplateView):
    template_name = "settings/control_panel.html"

    def get_context_data(self, **kwargs):
        context = super(SettingsOverview, self).get_context_data(**kwargs)
        syschk_cfg = get_syschk_cfg_params.delay().get()
        ossec_log = tailer_nline_from_file.delay(100).get()
        context['syschk_cfg'] = syschk_cfg
        context['ossec_log'] = ossec_log
        return context


class SettingsUpdate(RedirectView):
    url = reverse_lazy('settings:overview')

    def get_redirect_url(self, *args, **kwargs):
        syschk_cfg_fpath = self.request.GET.get('cfg_fpath', False)
        user_data_file_dirs = self.request.GET.get(
            'user_data_file_directories', False)
        system_cfg_file_dirs = self.request.GET.get(
            'system_cfg_file_directories', False)
        update_syschk_cfg_params.delay(
            syschk_cfg_fpath, user_data_file_dirs, system_cfg_file_dirs)
        return super().get_redirect_url(*args, **kwargs)
