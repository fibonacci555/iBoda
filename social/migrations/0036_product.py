# Generated by Django 4.1.1 on 2022-09-28 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0035_userprofile_favs_count_userprofile_public'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField(default=0)),
            ],
        ),
    ]