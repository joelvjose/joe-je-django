# Generated by Django 4.1.7 on 2023-03-31 05:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_images'),
        ('carts', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='cart_items',
            new_name='CartItems',
        ),
    ]
