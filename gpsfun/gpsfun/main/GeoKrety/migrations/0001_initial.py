# Generated by Django 3.1.2 on 2021-06-04 10:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('GeoMap', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoKret',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gkid', models.IntegerField(default=0)),
                ('waypoint', models.CharField(max_length=32, null=True)),
                ('type_code', models.CharField(max_length=2)),
                ('name', models.CharField(blank=True, max_length=128, null=True)),
                ('distance', models.IntegerField(default=0)),
                ('owner_id', models.IntegerField(null=True)),
                ('state', models.IntegerField(null=True)),
                ('image', models.CharField(blank=True, max_length=64, null=True)),
                ('country_code', models.CharField(blank=True, max_length=2, null=True)),
                ('admin_code', models.CharField(blank=True, max_length=6, null=True)),
                ('location', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='GeoMap.location')),
            ],
            options={
                'db_table': 'geokret',
            },
        ),
    ]