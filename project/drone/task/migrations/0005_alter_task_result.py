# Generated by Django 3.2.18 on 2023-05-13 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0004_alter_task_result'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='result',
            field=models.CharField(blank=True, default=None, max_length=1000),
            preserve_default=False,
        ),
    ]
