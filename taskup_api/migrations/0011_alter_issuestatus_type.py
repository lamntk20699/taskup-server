# Generated by Django 4.2 on 2024-07-13 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskup_api', '0010_issuehasuser_inmyissue_issuehasuser_intodo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuestatus',
            name='type',
            field=models.CharField(max_length=20),
        ),
    ]
