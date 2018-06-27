# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-27 08:58
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShpImport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shapefiles', models.FileField(help_text='Zipped shapefiles that contains .shp, .shx and .dbf files with a common filename prefix', upload_to='', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['zip'])], verbose_name='shapefiles')),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created time')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='created by')),
            ],
        ),
    ]
