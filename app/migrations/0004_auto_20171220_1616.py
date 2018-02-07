# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-20 15:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20171217_1613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='citations',
            field=models.ManyToManyField(null=True, related_name='postsCites', to='app.Citation'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pere',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.Post'),
        ),
        migrations.AlterField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(null=True, to='app.Tag'),
        ),
    ]
