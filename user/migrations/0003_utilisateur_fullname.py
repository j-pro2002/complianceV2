# Generated by Django 5.0.6 on 2024-07-04 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_utilisateur_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='fullname',
            field=models.CharField(default='Orange', max_length=255),
        ),
    ]
