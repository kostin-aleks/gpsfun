# Generated by Django 3.1.2 on 2022-05-24 10:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('GeoMap', '0002_auto_20210604_1130'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='EW_degree',
            new_name='ew_degree',
        ),
        migrations.RenameField(
            model_name='location',
            old_name='NS_degree',
            new_name='ns_degree',
        ),
    ]
