# Generated by Django 4.2.7 on 2023-11-19 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my1', '0002_busideacom'),
    ]

    operations = [
        migrations.AddField(
            model_name='busideacom',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Активно'),
        ),
    ]
