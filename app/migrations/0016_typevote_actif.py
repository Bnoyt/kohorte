# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-25 22:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_auto_20180212_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='typevote',
            name='actif',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]