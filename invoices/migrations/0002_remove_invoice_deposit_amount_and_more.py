# Generated by Django 5.1.7 on 2025-04-16 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='deposit_amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='deposit_paid',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='discount_amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='promo_code',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='rental_days',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='rental_price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='services_price',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='total_price',
        ),
    ]
