# Generated by Django 3.2.8 on 2022-08-31 05:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0022_post_reports'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='birthday',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='city',
        ),
    ]
