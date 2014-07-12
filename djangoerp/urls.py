#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

"""
This is a normal urlconf. it is imported from djangoerp.sites.site.get_url, where
the module views get appended by an '^module/' expression
"""

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth.views import logout
from django.utils import timezone
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.views.decorators.cache import cache_page
from django.views.decorators.http import last_modified
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView

from djangoerp.dashboard.views import DashboardView
from djangoerp.module.views import ModuleView
from djangoerp.modals.views import ModalSaveView
from djangoerp import get_version

# FIXME: Rewrite Tests and Forms to fully support AJAX - then DELETE THIS S**T
from django.http import HttpResponse
def status_ok(request):
    return HttpResponse('ok')

@cache_page(86400, key_prefix='erp-js18n-%s' % get_version())
@last_modified(lambda req, **kw: timezone.now())
def i18n_javascript(request):
    """
    Displays the i18n JavaScript that the Django admin requires.
    """
    if settings.USE_I18N:
        from django.views.i18n import javascript_catalog
    else:
        from django.views.i18n import null_javascript_catalog as javascript_catalog
    return javascript_catalog(request, packages=['djangoerp'])

urlpatterns = patterns('',
    url(r'^$', DashboardView.as_view(), name="dashboard"),
    url(r'^accounts/', include('djangoerp.account.urls')),
    url(r'^config/', include('djangoerp.configuration.urls')),
    url(r'^dashboard/', include('djangoerp.dashboard.urls')),
    url(r'^i18n/', i18n_javascript, name="jsi18n"),
#   url(r'^messages/', include('djangoerp.message.urls')),
    url(r'^notifications/', include('djangoerp.notification.urls')),
    url(r'^watching/', include('djangoerp.watch.urls')),
    url(r'^wizard/', include('djangoerp.wizard.urls')),
    #   r'^module/' via sites

    url(r'^status_ok$', status_ok, name="status_ok"), # FIXME

    # TODO
    url(r'^modules/$', ModuleView.as_view(), name="modules"),
    url(r'^ajax/save/view/$', ModalSaveView.as_view(), name="modal_saveview"),
    url(r'^activities/', include('djangoerp.activity.urls')),
    url(r'^file/', include('djangoerp.file.urls')),
)
