# Generated by Django 2.1.7 on 2019-03-28 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0004_auto_20190328_0020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='minute',
            field=models.IntegerField(default=25),
        ),
        migrations.AlterField(
            model_name='message',
            name='second',
            field=models.IntegerField(default=36),
        ),
        migrations.AlterField(
            model_name='message',
            name='user',
            field=models.CharField(default='user', max_length=32),
        ),
    ]
