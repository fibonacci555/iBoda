# Generated by Django 4.1.1 on 2022-10-11 16:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField(default=0)),
                ('file', models.FileField(blank=True, null=True, upload_to='product_files/')),
                ('url', models.URLField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('verified', models.BooleanField(default=False)),
                ('picture', models.ImageField(blank=True, default='uploads/profile_pictures/default.jpg', upload_to='uploads/profile_pictures')),
                ('public', models.BooleanField(default=True)),
                ('favs_count', models.PositiveIntegerField(default=0)),
                ('birth', models.DateField(default='2002-09-03')),
                ('city', models.CharField(default='', max_length=40)),
                ('follow_requests', models.PositiveIntegerField(default=0)),
                ('followers', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=70)),
                ('city', models.CharField(default='', max_length=40)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('body', models.TextField()),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to='uploads/post_photos')),
                ('music', models.CharField(default='', max_length=70)),
                ('url', models.URLField(blank=True, null=True)),
                ('age', models.CharField(default='', max_length=70)),
                ('approved', models.BooleanField(default=True)),
                ('likes_count', models.PositiveIntegerField(default=0)),
                ('public', models.BooleanField(default=True)),
                ('comments', models.PositiveIntegerField(default=0)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('favs', models.ManyToManyField(blank=True, related_name='favs', to=settings.AUTH_USER_MODEL)),
                ('likes', models.ManyToManyField(blank=True, related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('reports', models.ManyToManyField(blank=True, related_name='reports', to=settings.AUTH_USER_MODEL)),
                ('saves', models.ManyToManyField(blank=True, related_name='saves', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(blank=True, default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='social.comment')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.post')),
            ],
        ),
    ]
