# Generated by Django 4.2.8 on 2024-02-28 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cloudtrailapp', '0008_alter_cloudtrailrecord_resource'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cloudtrailrecord',
            old_name='Resource',
            new_name='ResourceName',
        ),
    ]
