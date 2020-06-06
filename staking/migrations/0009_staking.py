# Generated by Django 3.0.6 on 2020-06-06 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staking', '0008_binding'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('timestamp', models.CharField(max_length=100)),
            ],
        ),
    ]
