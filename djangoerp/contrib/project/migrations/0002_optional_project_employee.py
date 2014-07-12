# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from djangoerp.settings import BASE_MODULE

if BASE_MODULE["EMPLOYEE"]:
    class Migration(migrations.Migration):
        dependencies = [
            ('djangoerp_project', '0001_initial'),
            migrations.swappable_dependency(BASE_MODULE["EMPLOYEE"]),
        ]
        operations = [
            migrations.AddField(
                model_name='project',
                name='employee',
                field=models.ForeignKey(to=BASE_MODULE["EMPLOYEE"], null=True, blank=True),
                preserve_default=True,
            ),
        ]
else:
    class Migration(migrations.Migration):
        pass
