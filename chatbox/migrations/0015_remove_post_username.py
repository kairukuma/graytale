# Generated by Django 2.1.7 on 2019-04-29 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0014_auto_20190429_0039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='username',
        ),
    ]