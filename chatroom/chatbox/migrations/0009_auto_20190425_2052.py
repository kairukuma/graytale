# Generated by Django 2.1.7 on 2019-04-26 00:52

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chatbox', '0008_auto_20190425_2043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notification',
            name='user',
        ),
        migrations.AddField(
            model_name='notification',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='message',
            name='datetime',
            field=models.IntegerField(default=1556239924.0),
        ),
        migrations.AlterField(
            model_name='post',
            name='datetime',
            field=models.IntegerField(default=1556239924.0),
        ),
    ]
