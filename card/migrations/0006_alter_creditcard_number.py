# Generated by Django 3.2.6 on 2021-10-28 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card', '0005_alter_creditcard_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditcard',
            name='number',
            field=models.CharField(blank=True, max_length=16, null=True),
        ),
    ]
