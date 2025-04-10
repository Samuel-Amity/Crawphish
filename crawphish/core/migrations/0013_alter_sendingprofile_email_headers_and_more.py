# Generated by Django 5.1.7 on 2025-04-02 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_emailtemplate_attachments_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sendingprofile',
            name='email_headers',
            field=models.JSONField(default=dict, help_text='Additional email headers in JSON format.'),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='host',
            field=models.CharField(help_text='The SMTP server host.', max_length=255),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='ignore_cert_errors',
            field=models.BooleanField(default=False, help_text='Ignore certificate errors when connecting to the SMTP server.'),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='interface_type',
            field=models.CharField(help_text='The type of email interface (e.g., SMTP, API).', max_length=50),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='name',
            field=models.CharField(help_text='A unique name for this sending profile.', max_length=100),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='password',
            field=models.CharField(help_text='Password for SMTP authentication.', max_length=255),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='port',
            field=models.IntegerField(default=587, help_text='The SMTP server port (default is 587 for TLS).'),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='smtp_from',
            field=models.CharField(help_text="The email address that will appear in the 'From' field.", max_length=255),
        ),
        migrations.AlterField(
            model_name='sendingprofile',
            name='username',
            field=models.CharField(help_text='Username for SMTP authentication.', max_length=255),
        ),
    ]
