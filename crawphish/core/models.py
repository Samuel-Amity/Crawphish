from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.utils import timezone
import uuid

class User(AbstractUser):
    position = models.CharField(max_length=100, blank=True, null=True)
    api_key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def generate_api_key(self):
        self.api_key = str(uuid.uuid4())
        self.save()
        return self.api_key

class ExternalUser(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('ExternalUser', related_name='groups')
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

class ClickerGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField('ExternalUser', related_name='clicker_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class SubmitterGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField('ExternalUser', related_name='submitter_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)
    plain_content = models.TextField(blank=True)
    envelope_sender = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    html_content = models.TextField(blank=True)
    add_tracking_image = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now=True)
    difficulty = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
        help_text="Difficulty level from 1 (easy to spot) to 5 (hard to spot)"
    )

    def __str__(self):
        return self.name

    def get_edit_url(self):
        return reverse('core:email_template_edit', kwargs={'pk': self.pk})

    def get_absolute_url(self):
        return reverse('core:email_templates')

class Attachment(models.Model):
    email_template = models.ForeignKey(EmailTemplate, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='email_template_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

class LandingPage(models.Model):
    name = models.CharField(max_length=100)
    html_content = models.TextField()
    capture_submitted_data = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SendingProfile(models.Model):
    INTERFACE_TYPES = (
        ('smtp', 'SMTP'),
        ('api', 'API'),
    )
    API_PROVIDERS = (
        ('sendgrid', 'SendGrid'),
        # Add more providers like ('mailgun', 'Mailgun') as needed
    )
    name = models.CharField(max_length=100, help_text="Unique name for this profile.")
    interface_type = models.CharField(max_length=50, choices=INTERFACE_TYPES, help_text="SMTP or API.")
    smtp_from = models.CharField(max_length=255, help_text="From email address.")
    # SMTP fields
    host = models.CharField(max_length=255, blank=True, null=True, help_text="SMTP server host.")
    port = models.IntegerField(blank=True, null=True, help_text="SMTP server port.")
    username = models.CharField(max_length=255, blank=True, null=True, help_text="SMTP username.")
    password = models.CharField(max_length=255, blank=True, null=True, help_text="SMTP password.")
    # API fields
    api_key = models.CharField(max_length=200, blank=True, null=True, help_text="API key for API sending.")
    api_provider = models.CharField(max_length=50, choices=API_PROVIDERS, blank=True, null=True, help_text="API provider (e.g., SendGrid).")
    ignore_cert_errors = models.BooleanField(default=False, help_text="Ignore SMTP cert errors.")
    email_headers = models.JSONField(default=dict, help_text="Additional email headers.")
    is_default = models.BooleanField(default=False, help_text="Mark as a default profile.")
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class CampaignGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email_template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    landing_page = models.ForeignKey('LandingPage', on_delete=models.SET_NULL, null=True, blank=True)
    sending_profile = models.ForeignKey('SendingProfile', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('archived', 'Archived'),
    )
    FREQUENCY_CHOICES = (
        ('one_time', 'One Time'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    )
    SENDING_PERIOD_CHOICES = (
        ('immediate', 'Immediate'),
        ('over_period', 'Over a Period'),
    )

    name = models.CharField(max_length=100)
    campaign_group = models.ForeignKey(CampaignGroup, on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField()
    launch_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    sending_profile = models.ForeignKey('SendingProfile', on_delete=models.CASCADE)
    groups = models.ManyToManyField('Group', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    send_to_all_users = models.BooleanField(
        default=False,
        help_text="If checked, sends to all ExternalUsers; if unchecked, sends to selected groups"
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='one_time',
        help_text="How often the campaign should run"
    )
    sending_period_type = models.CharField(
        max_length=20,
        choices=SENDING_PERIOD_CHOICES,
        default='immediate',
        help_text="Whether emails are sent all at once or spread out"
    )
    sending_period_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of days to spread sending if 'Over a Period' is selected"
    )
    track_activity_duration = models.PositiveIntegerField(
        default=3,
        help_text="Number of days to track user activity after the campaign ends"
    )
    track_replied_emails = models.BooleanField(
        default=False,
        help_text="Track if users reply to the phishing email"
    )
    email_templates = models.ManyToManyField(
        'EmailTemplate',
        help_text="Multiple email templates to choose from during the campaign"
    )
    landing_pages = models.ManyToManyField(
        'LandingPage',
        help_text="Multiple landing pages to show after a click"
    )
    clicker_groups = models.ManyToManyField(
        'ClickerGroup',
        blank=True,
        help_text="Groups to add users who click links"
    )
    submitter_groups = models.ManyToManyField(
        'SubmitterGroup',
        blank=True,
        help_text="Groups to add users who enter passwords"
    )
    send_report_after_end = models.BooleanField(
        default=False,
        help_text="Send an email report when the campaign ends"
    )
    hide_from_dashboard = models.BooleanField(
        default=False,
        help_text="Hide campaign data from the dashboard"
    )

    def __str__(self):
        return self.name

class CampaignEvent(models.Model):
    EVENT_TYPES = (
        ('sent', 'Email Sent'),
        ('opened', 'Email Opened'),
        ('clicked', 'Link Clicked'),
        ('submitted', 'Data Submitted'),
        ('reported', 'Email Reported'),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='events')
    user = models.ForeignKey('ExternalUser', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    email_template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    landing_page = models.ForeignKey('LandingPage', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.event_type} - {self.campaign.name} - {self.user.email}"

class Webhook(models.Model):

    name = models.CharField(max_length=100)
    url = models.URLField()
    events = models.JSONField(default=list)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    



# class sattu(models.Model):

#     pass