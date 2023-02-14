# Generated by Django 3.2.6 on 2021-10-20 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0004_alter_movie_expire_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='show_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('row', models.CharField(default='A', max_length=10)),
                ('number', models.IntegerField(default=1)),
                ('price', models.IntegerField(default=10)),
                ('room', models.CharField(default='A', max_length=10)),
                ('show', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='movie.show')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
