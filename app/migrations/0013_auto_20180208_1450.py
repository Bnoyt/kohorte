# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-08 14:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20180201_1105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lienpostssgraphe',
            name='typeLien',
        ),
        migrations.DeleteModel(
            name='lienPostsSgraphe',
        ),
        migrations.DeleteModel(
            name='TypeLienSg',
        ),
    ]
