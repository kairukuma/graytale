# Generated by Django 2.1.7 on 2019-04-20 01:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0005_auto_20190407_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='datetime',
            field=models.IntegerField(default=1555723837.0),
        ),
        migrations.AlterField(
            model_name='post',
            name='datetime',
            field=models.IntegerField(default=1555723837.0),
        ),
    ]
