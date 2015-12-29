#!/usr/bin/python
# ex:set fileencoding=utf-8:

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
# from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.http import Http404
from django.utils.decorators import method_decorator
from django.utils.text import force_text
from django.utils.timezone import now
from django.views.defaults import permission_denied
from django.views.generic import CreateView
from django.views.generic import ListView
from django.views.generic import UpdateView

from djangobmf.conf import settings
from djangobmf.models import Activity
from djangobmf.models import Notification
from djangobmf.views.mixins import ViewMixin
from djangobmf.views.mixins import AjaxMixin
from djangobmf.signals import activity_comment

import logging
logger = logging.getLogger(__name__)


class NotificationView(ViewMixin, ListView):
    model = Notification
    allow_empty = True
    template_name = "djangobmf/notification/index.html"
    paginate_by = 50

    def get_context_data(self, **kwargs):
        selected_ct_id = int(self.kwargs.get('ct', 0))
        selected_model = None

        # Dict with all items of right navigation
        navigation = {}

        from djangobmf.sites import site

        # prefill
        for ct, model in site.models.items():
            info = model._meta.app_label, model._meta.model_name
            perm = '%s.view_%s' % info

            if ct == selected_ct_id:
                selected_model = model

            if model._bmfmeta.has_activity:
                navigation[ct] = {
                    'name': force_text(model._meta.verbose_name_plural),
                    'count': 0,
                    'ct': ct,
                    'visible': self.request.user.has_perm(perm),
                }

        total = 0
        qs = Notification.objects.exclude(watch_id__isnull=True).filter(user=self.request.user, unread=True)
        # FIXME: The query used here should use SQL to distinct select and count the db
        for data in qs.annotate(count=Count('unread')).values('watch_ct', 'count'):
            navigation[data['watch_ct']]['visible'] = True
            navigation[data['watch_ct']]['count'] += data['count']
            total += data['count']

        # update notification icon if neccessary
        sessiondata = self.request.session.get('djangobmf', None)
        if sessiondata and total != sessiondata.get('notification_count', -1):
            self.update_notification(total)

        kwargs.update({
            'navigation': navigation.values(),
            'model_name': selected_model._meta.model_name if selected_model else 'none',
            'app_label': selected_model._meta.app_label if selected_model else 'none',
            'unread': total,
            'selected_ct': selected_ct_id,
            'datafilter': self.kwargs.get('filter', None),
            'symbols': {
                'workflow': settings.ACTIVITY_WORKFLOW,
                'comment': settings.ACTIVITY_COMMENT,
                'updated': settings.ACTIVITY_UPDATED,
                'file': settings.ACTIVITY_FILE,
                'created': settings.ACTIVITY_CREATED,
            }
        })

        # load settings for specific category
        if selected_model and navigation[selected_ct_id]['visible']:
            default, created = Notification.objects.get_or_create(
                user=self.request.user,
                watch_ct_id=selected_ct_id,
                watch_id=None,
                unread=False,
            )

            if created:
                logger.debug("Notifications object (%s) created for %s" % (default.pk, self.request.user))

            kwargs.update({
                'glob_settings': default,
                'has_detectchanges': selected_model._bmfmeta.has_detectchanges,
                'has_files': selected_model._bmfmeta.has_files,
                'has_comments': selected_model._bmfmeta.has_comments,
                'has_workflow': selected_model._bmfmeta.has_workflow,
            })

        return super(NotificationView, self).get_context_data(**kwargs)

    def get_queryset(self):

        qs = Notification.objects.exclude(watch_id__isnull=True).filter(user=self.request.user)

        filter = self.kwargs.get('filter', "unread")

        if filter == "unread":
            qs = qs.filter(unread=True)

        if filter == "active":
            qs = qs.filter(triggered=True)

        if self.kwargs.get('ct', None):
            qs = qs.filter(watch_ct_id=self.kwargs.get('ct'))

        return qs.select_related('watch_ct')
