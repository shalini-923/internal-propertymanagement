# Generated by Django 5.1.2 on 2024-10-24 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('property', '0005_landlord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='property',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
