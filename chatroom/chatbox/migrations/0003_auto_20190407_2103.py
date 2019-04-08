# Generated by Django 2.1.7 on 2019-04-08 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0002_auto_20190407_2102'),
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=48)),
            ],
        ),
        migrations.AlterField(
            model_name='message',
            name='datetime',
            field=models.IntegerField(default=1554685406.0),
        ),
        migrations.AlterField(
            model_name='post',
            name='datetime',
            field=models.IntegerField(default=1554685406.0),
        ),
    ]
