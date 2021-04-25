# Generated by Django 3.1.2 on 2021-04-25 23:11

from django.db import migrations, models
import django.db.models.deletion
import gpsfun.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GeoPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, default=0, max_digits=10, verbose_name='latitude')),
                ('longitude', models.DecimalField(decimal_places=6, default=0, max_digits=10, verbose_name='longitude')),
            ],
            options={
                'verbose_name': 'geopoint',
                'verbose_name_plural': 'geopoints',
                'db_table': 'geopoint',
            },
        ),
        migrations.CreateModel(
            name='Peak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('map_image', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='map')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='photo')),
                ('point', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='Carpathians.geopoint', verbose_name='point')),
            ],
            options={
                'verbose_name': 'peak',
                'verbose_name_plural': 'peaks',
                'db_table': 'peak',
            },
        ),
        migrations.CreateModel(
            name='Ridge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('map_image', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='map')),
            ],
            options={
                'verbose_name': 'ridge',
                'verbose_name_plural': 'ridges',
                'db_table': 'ridge',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField(blank=True, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='photo')),
                ('difficulty', models.CharField(max_length=32)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('author', models.CharField(blank=True, max_length=64, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('height_difference', models.IntegerField(blank=True, null=True)),
                ('start_height', models.IntegerField(blank=True, null=True)),
                ('peak', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.peak', verbose_name='peak')),
            ],
            options={
                'verbose_name': 'route',
                'verbose_name_plural': 'routes',
                'db_table': 'route',
            },
        ),
        migrations.CreateModel(
            name='RouteSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.IntegerField(blank=True, null=True)),
                ('length', models.IntegerField(blank=True, null=True)),
                ('angle', models.CharField(blank=True, max_length=32, null=True)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.route', verbose_name='route')),
            ],
            options={
                'verbose_name': 'route section',
                'verbose_name_plural': 'route sections',
                'db_table': 'route_section',
            },
        ),
        migrations.CreateModel(
            name='RoutePhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='photo')),
                ('description', models.CharField(max_length=128)),
                ('route', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.route', verbose_name='route')),
            ],
            options={
                'verbose_name': 'route photo',
                'verbose_name_plural': 'route photos',
                'db_table': 'route_photo',
            },
        ),
        migrations.CreateModel(
            name='RidgeInfoLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.URLField(blank=True, max_length=128, verbose_name='link')),
                ('description', models.CharField(max_length=128)),
                ('ridge', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.ridge', verbose_name='ridge')),
            ],
            options={
                'verbose_name': 'ridge link',
                'verbose_name_plural': 'ridge links',
                'db_table': 'ridge_info_link',
            },
        ),
        migrations.CreateModel(
            name='PeakPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, null=True, upload_to=gpsfun.utils.get_image_path, verbose_name='photo')),
                ('description', models.CharField(max_length=128)),
                ('peak', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.peak', verbose_name='peak')),
            ],
            options={
                'verbose_name': 'peak photo',
                'verbose_name_plural': 'peak photos',
                'db_table': 'peak_photo',
            },
        ),
        migrations.AddField(
            model_name='peak',
            name='ridge',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='Carpathians.ridge', verbose_name='ridge'),
        ),
    ]
