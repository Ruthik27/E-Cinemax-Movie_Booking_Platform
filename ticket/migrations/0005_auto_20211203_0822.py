# Generated by Django 3.2.6 on 2021-12-03 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0004_booking_seat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='seat',
        ),
        migrations.AddField(
            model_name='booking',
            name='seat_rows',
            field=models.TextField(blank=True, null=True),
        ),
    ]
