# Generated by Django 2.1.7 on 2019-04-03 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0011_auto_20190403_1254'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='datetime',
            field=models.IntegerField(default=1554311034.0),
        ),
        migrations.AlterField(
            model_name='message',
            name='datetime',
            field=models.IntegerField(default=1554311034.0),
        ),
    ]
