# Generated by Django 3.0.2 on 2020-01-23 09:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('altroochat', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messagemodel',
            options={'ordering': ('-created',), 'verbose_name': 'message', 'verbose_name_plural': 'messages'},
        ),
        migrations.RemoveField(
            model_name='messagemodel',
            name='timestamp',
        ),
        migrations.AddField(
            model_name='messagemodel',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, default=django.utils.timezone.now, verbose_name='created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='messagemodel',
            name='updated',
            field=models.DateTimeField(auto_now=True, verbose_name='updated'),
        ),
        migrations.AddField(
            model_name='messagemodel',
            name='viewed_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]