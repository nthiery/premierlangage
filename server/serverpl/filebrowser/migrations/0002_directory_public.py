# Generated by Django 2.0.4 on 2018-05-25 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filebrowser', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='directory',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
