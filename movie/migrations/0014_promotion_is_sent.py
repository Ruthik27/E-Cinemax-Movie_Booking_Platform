# Generated by Django 3.2.6 on 2021-11-17 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0013_alter_promotion_promo_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotion',
            name='is_sent',
            field=models.BooleanField(default=False),
        ),
    ]
