# Generated by Django 3.2.18 on 2023-05-13 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0005_alter_task_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='result',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
