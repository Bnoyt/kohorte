# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-14 23:57
from __future__ import unicode_literals

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='contenu',
            field=markdownx.models.MarkdownxField(),
        ),
        migrations.AlterField(
            model_name='postversionne',
            name='contenu',
            field=markdownx.models.MarkdownxField(),
        ),
    ]
