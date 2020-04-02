# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView, RedirectView
from django.views import defaults as default_views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/dashboard/', permanent=False)),
    url(r'^statistics/$', TemplateView.as_view(template_name='pages/statistics.html'), name='statistics'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('yosim.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    # YOSIM urls
    url(r'^servers/', include('yosim.servers.urls', namespace='servers')),
    url(r'^agents/', include('yosim.agents.urls', namespace='agents')),
    url(r'^rules/', include('yosim.rules.urls', namespace='rules')),
    url(r'^locations/', include('yosim.locations.urls', namespace='locations')),
    url(r'^categories/', include('yosim.categories.urls', namespace='categories')),
    url(r'^signatures/', include('yosim.signatures.urls', namespace='signatures')),
    url(r'^alerts/', include('yosim.alerts.urls', namespace='alerts')),
    url(r'^syschecks/', include('yosim.syschecks.urls', namespace='syschecks')),
    url(r'^dashboard/', include('yosim.dashboard.urls', namespace='dashboard')),
    url(r'^settings/', include('yosim.settings.urls', namespace='settings')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
