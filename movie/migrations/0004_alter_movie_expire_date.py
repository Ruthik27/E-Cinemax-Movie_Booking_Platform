# Generated by Django 3.2.6 on 2021-10-01 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0003_alter_movie_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='expire_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
