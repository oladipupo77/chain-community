# Generated by Django 4.0.3 on 2022-03-10 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_bid_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='status',
        ),
    ]
