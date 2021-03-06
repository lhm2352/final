# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-22 05:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredientName', models.CharField(max_length=50)),
                ('type', models.IntegerField(default=0)),
                ('category', models.IntegerField(default=0)),
                ('storageMethod', models.IntegerField(default=0)),
                ('unit', models.CharField(max_length=100)),
                ('defaultValue', models.IntegerField(default=0)),
                ('ingredientCode', models.IntegerField(default=0)),
            ],
        ),
    ]
