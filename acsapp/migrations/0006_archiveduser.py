# Generated by Django 5.1.1 on 2024-09-18 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acsapp', '0005_deletedtask'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchivedUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('date_joined', models.DateTimeField()),
                ('deleted_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
