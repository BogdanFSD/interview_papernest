# Generated by Django 4.2.18 on 2025-01-17 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoverageData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operator', models.CharField(max_length=50)),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('g2', models.BooleanField()),
                ('g3', models.BooleanField()),
                ('g4', models.BooleanField()),
            ],
        ),
    ]
