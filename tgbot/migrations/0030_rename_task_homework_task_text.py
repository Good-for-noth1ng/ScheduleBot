# Generated by Django 4.0.3 on 2022-04-05 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0029_homework_name_homework_task_alter_homework_task_doc'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homework',
            old_name='task',
            new_name='task_text',
        ),
    ]