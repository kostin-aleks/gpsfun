# Generated by Django 3.1.2 on 2021-04-28 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Carpathians', '0008_auto_20210428_2149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='short_description',
            field=models.TextField(blank=True, null=True),
        ),
    ]