# Generated by Django 5.0.7 on 2024-08-02 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_remove_customuser_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='amount',
            field=models.IntegerField(default=0),
        ),
    ]
