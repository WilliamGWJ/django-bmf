# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

from djangoerp.settings import BASE_MODULE

if BASE_MODULE["EMPLOYEE"]:
    class Migration(migrations.Migration):
        dependencies = [
            ('djangoerp_position', '0001_initial'),
            migrations.swappable_dependency(BASE_MODULE["EMPLOYEE"]),
        ]
        operations = [
            migrations.AddField(
                model_name='position',
                name='employee',
                field=models.ForeignKey(to=BASE_MODULE["EMPLOYEE"], null=True),
                preserve_default=True,
            ),
        ]
else:
    class Migration(migrations.Migration):
        pass
