# Generated by Django 5.1.4 on 2025-01-01 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('back', '0002_remove_quiz_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
