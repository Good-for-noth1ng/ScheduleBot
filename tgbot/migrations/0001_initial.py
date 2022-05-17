# Generated by Django 4.0.3 on 2022-05-17 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('url', models.URLField(default='', max_length=500)),
                ('is_link_to_book', models.BooleanField(default=False)),
                ('is_link_to_command', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='InternalResource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=2000)),
                ('text', models.CharField(default='', max_length=5000)),
                ('is_requirement', models.BooleanField(default=False)),
                ('is_homework', models.BooleanField(default=False)),
                ('is_solution', models.BooleanField(default=False)),
                ('is_schedule', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Пн', 'Monday'), ('Вт', 'Tuesday'), ('Ср', 'Wednsday'), ('Чт', 'Thursday'), ('Пт', 'Friday'), ('Сб', 'Saturday')], default='', max_length=2)),
                ('time', models.CharField(choices=[('8:30', 'First'), ('10:10', 'Second'), ('11:50', 'Third'), ('13:50', 'Fourth'), ('15:30', 'Fifth'), ('17:10', 'Sixth'), ('18:50', 'Seventh'), ('+', 'Eighth')], default='', max_length=5)),
                ('lesson', models.CharField(default='', max_length=200)),
                ('group', models.CharField(default='', max_length=200)),
                ('teacher', models.CharField(default='', max_length=200)),
                ('isOnline', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(blank=True, max_length=256, null=True)),
                ('deep_link', models.CharField(blank=True, max_length=64, null=True)),
                ('is_blocked_bot', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InternalResourceFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_id', models.CharField(default='', max_length=500)),
                ('file_id', models.CharField(default='', max_length=500)),
                ('internal_resource', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tgbot.internalresource')),
            ],
        ),
    ]
