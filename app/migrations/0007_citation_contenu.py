# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-03 00:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20171229_1817'),
    ]

    operations = [
        migrations.AddField(
            model_name='citation',
            name='contenu',
            field=models.TextField(default=None),
        ),
    ]
