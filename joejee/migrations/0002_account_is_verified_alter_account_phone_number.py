# Generated by Django 4.1.7 on 2023-03-28 07:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('joejee', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='account',
            name='phone_number',
            field=models.TextField(max_length=20),
        ),
    ]
