# Generated by Django 3.2.8 on 2021-10-14 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_entry_date_added'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='rating',
            field=models.PositiveIntegerField(choices=[(5, 'Very Good'), (4, 'Good'), (3, 'Neutral'), (2, 'Bad'), (1, 'Very Bad')], default=1),
        ),
    ]
