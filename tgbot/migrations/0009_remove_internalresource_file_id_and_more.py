# Generated by Django 4.0.3 on 2022-04-30 13:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0008_remove_externalresource_category_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='internalresource',
            name='file_id',
        ),
        migrations.RemoveField(
            model_name='internalresource',
            name='photo_id',
        ),
    ]
