# Generated by Django 5.1.2 on 2024-10-18 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0002_propertytype_remove_property_property_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='property',
            old_name='email',
            new_name='contact_email',
        ),
    ]
