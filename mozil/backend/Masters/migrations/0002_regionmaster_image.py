# Generated by Django 5.2 on 2025-06-07 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Masters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='regionmaster',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='master/region/images/', verbose_name='region Image'),
        ),
    ]
