# Generated by Django 2.0.6 on 2018-06-12 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qa', '0013_auto_20180610_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qaanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_set', to='qa.QAQuestion'),
        ),
    ]