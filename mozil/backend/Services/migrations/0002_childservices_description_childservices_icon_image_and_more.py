# Generated by Django 5.2 on 2025-04-19 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='childservices',
            name='Description',
            field=models.CharField(blank=True, max_length=1150, null=True),
        ),
        migrations.AddField(
            model_name='childservices',
            name='icon_image',
            field=models.FileField(blank=True, null=True, upload_to='services/child/icon_image/', verbose_name='icon Image'),
        ),
        migrations.AddField(
            model_name='parentservices',
            name='Description',
            field=models.CharField(blank=True, max_length=1150, null=True),
        ),
        migrations.AddField(
            model_name='parentservices',
            name='icon_image',
            field=models.FileField(blank=True, null=True, upload_to='services/parent/icon_image/', verbose_name='icon Image'),
        ),
    ]
