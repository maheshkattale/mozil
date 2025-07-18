# Generated by Django 5.2 on 2025-05-25 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegionMaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdAt', models.DateTimeField(auto_now_add=True, null=True)),
                ('updatedAt', models.DateTimeField(blank=True, null=True)),
                ('createdBy', models.CharField(blank=True, max_length=255, null=True)),
                ('updatedBy', models.CharField(blank=True, max_length=255, null=True)),
                ('isActive', models.BooleanField(blank=True, default=True, null=True)),
                ('deletedBy', models.CharField(blank=True, max_length=255, null=True)),
                ('deletedAt', models.DateTimeField(blank=True, null=True)),
                ('viewedBy', models.CharField(blank=True, max_length=255, null=True)),
                ('viewedAt', models.DateTimeField(blank=True, null=True)),
                ('Name', models.CharField(blank=True, max_length=250, null=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-createdAt',),
                'abstract': False,
            },
        ),
    ]
