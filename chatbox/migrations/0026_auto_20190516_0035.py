# Generated by Django 2.1.7 on 2019-05-16 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chatbox', '0025_auto_20190515_0046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(blank=True, max_length=50000),
        ),
    ]