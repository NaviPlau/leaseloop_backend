# Generated by Django 5.1.7 on 2025-05-22 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lease_auth', '0003_profile_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlogo',
            name='logo',
            field=models.FileField(blank=True, null=True, upload_to='logos/'),
        ),
    ]
