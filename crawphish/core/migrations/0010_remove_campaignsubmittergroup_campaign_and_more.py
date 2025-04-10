# Generated by Django 5.1.7 on 2025-03-30 12:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_remove_campaign_clicker_groups_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campaignsubmittergroup',
            name='campaign',
        ),
        migrations.RemoveField(
            model_name='campaignsubmittergroup',
            name='group',
        ),
        migrations.CreateModel(
            name='CampaignUserGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_type', models.CharField(choices=[('clicker', 'Clicker'), ('submitter', 'Submitter')], help_text='Specify if the group is for clickers or submitters.', max_length=10)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_entries', to='core.campaign')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.group')),
            ],
        ),
        migrations.DeleteModel(
            name='CampaignClickerGroup',
        ),
        migrations.DeleteModel(
            name='CampaignSubmitterGroup',
        ),
    ]
