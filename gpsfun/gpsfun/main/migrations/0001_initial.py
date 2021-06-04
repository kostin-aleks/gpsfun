# Generated by Django 3.1.2 on 2021-06-04 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogAPI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=32)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('IP', models.CharField(max_length=16)),
            ],
            options={
                'db_table': 'log_api',
            },
        ),
        migrations.CreateModel(
            name='LogCheckData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geocacher_count', models.IntegerField(blank=True, null=True)),
                ('geocacher_wo_country_count', models.IntegerField(blank=True, null=True)),
                ('geocacher_wo_region_count', models.IntegerField(blank=True, null=True)),
                ('cache_count', models.IntegerField(blank=True, null=True)),
                ('cache_wo_country_count', models.IntegerField(blank=True, null=True)),
                ('cache_wo_region_count', models.IntegerField(blank=True, null=True)),
                ('cache_wo_author_count', models.IntegerField(blank=True, null=True)),
                ('checking_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'log_check_data',
            },
        ),
        migrations.CreateModel(
            name='LogUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_type', models.CharField(max_length=32)),
                ('update_date', models.DateTimeField(blank=True, null=True)),
                ('message', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'log_update',
            },
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'variables',
            },
        ),
    ]
