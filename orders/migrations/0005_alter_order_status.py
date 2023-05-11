# Generated by Django 4.1.7 on 2023-04-24 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_remove_orderproduct_colour_remove_orderproduct_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('New', 'New'), ('Confirmed', 'Confirmed'), ('shipping', 'shipping'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='New', max_length=50),
        ),
    ]
