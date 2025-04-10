# Generated by Django 5.1.7 on 2025-03-30 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_campaigngroup_campaign_campaign_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaign',
            name='email_template',
        ),
        migrations.RemoveField(
            model_name='campaign',
            name='landing_page',
        ),
        migrations.AddField(
            model_name='campaign',
            name='clicker_groups',
            field=models.ManyToManyField(blank=True, help_text='Groups to add users who click links', related_name='campaigns_clickers', to='core.group'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='email_templates',
            field=models.ManyToManyField(help_text='Multiple email templates to choose from during the campaign', to='core.emailtemplate'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='frequency',
            field=models.CharField(choices=[('one_time', 'One Time'), ('weekly', 'Weekly'), ('biweekly', 'Biweekly'), ('monthly', 'Monthly'), ('quarterly', 'Quarterly'), ('yearly', 'Yearly')], default='one_time', help_text='How often the campaign should run', max_length=20),
        ),
        migrations.AddField(
            model_name='campaign',
            name='hide_from_dashboard',
            field=models.BooleanField(default=False, help_text='Hide campaign data from the dashboard'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='landing_pages',
            field=models.ManyToManyField(help_text='Multiple landing pages to show after a click', to='core.landingpage'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='send_report_after_end',
            field=models.BooleanField(default=False, help_text='Send an email report when the campaign ends'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='send_to_all_users',
            field=models.BooleanField(default=False, help_text='If True, sends to all ExternalUsers; if False, sends to selected groups'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='sending_period_days',
            field=models.PositiveIntegerField(blank=True, help_text="Number of days to spread sending if 'Over a Period' is selected", null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='sending_period_type',
            field=models.CharField(choices=[('immediate', 'Immediate'), ('over_period', 'Over a Period')], default='immediate', help_text='Whether emails are sent all at once or spread out', max_length=20),
        ),
        migrations.AddField(
            model_name='campaign',
            name='submitter_groups',
            field=models.ManyToManyField(blank=True, help_text='Groups to add users who enter passwords', related_name='campaigns_submitters', to='core.group'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='track_activity_duration',
            field=models.PositiveIntegerField(default=3, help_text='Number of days to track user activity after each send'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='track_replied_emails',
            field=models.BooleanField(default=False, help_text='Track if users reply to the phishing email'),
        ),
        migrations.AddField(
            model_name='emailtemplate',
            name='difficulty',
            field=models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], default=1, help_text='Difficulty level from 1 (easy to spot) to 5 (hard to spot)'),
        ),
        migrations.AlterField(
            model_name='campaign',
            name='groups',
            field=models.ManyToManyField(blank=True, to='core.group'),
        ),
    ]
