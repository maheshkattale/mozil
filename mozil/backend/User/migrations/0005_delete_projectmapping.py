# Generated by Django 5.2 on 2025-04-09 19:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0004_serviceprovider_average_rating_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectMapping',
        ),
    ]
