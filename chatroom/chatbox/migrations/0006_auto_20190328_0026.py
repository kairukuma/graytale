# Generated by Django 2.1.7 on 2019-03-28 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0005_auto_20190328_0025'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='user',
            new_name='username',
        ),
        migrations.AlterField(
            model_name='message',
            name='minute',
            field=models.IntegerField(default=26),
        ),
        migrations.AlterField(
            model_name='message',
            name='second',
            field=models.IntegerField(default=1),
        ),
    ]
