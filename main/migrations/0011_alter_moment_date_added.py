# Generated by Django 3.2.8 on 2021-10-25 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_alter_entry_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moment',
            name='date_added',
            field=models.DateTimeField(),
        ),
    ]
