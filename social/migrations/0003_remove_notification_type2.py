# Generated by Django 4.1.1 on 2022-10-11 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0002_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='type2',
        ),
    ]
