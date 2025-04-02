# from celery import shared_task
# from django.core.mail import EmailMultiAlternatives
# from django.template import Template, Context
# from django.core.signing import Signer
# from .models import Campaign, CampaignEvent

# signer = Signer()

# @shared_task
# def send_campaign_emails(campaign_id):
#     campaign = Campaign.objects.get(id=campaign_id)
#     email_template = campaign.email_template
#     sending_profile = campaign.sending_profile
#     recipients = ExternalUser.objects.filter(groups__in=campaign.groups.all()).distinct()

#     for recipient in recipients:
#         token = signer.sign(f"{campaign.id}:{recipient.id}")
#         base_url = "http://yourdomain.com"  # Replace with your domain
#         tracking_pixel = f"{base_url}/track/open/{token}/"
#         tracking_link = f"{base_url}/track/click/{token}/"

#         context = {
#             'first_name': recipient.first_name,
#             'last_name': recipient.last_name,
#             'tracking_pixel': tracking_pixel,
#             'tracking_link': tracking_link,
#         }
#         html_template = Template(email_template.html_content)
#         html_content = html_template.render(Context(context))
#         text_content = email_template.plain_content or "Please view this email in HTML."

#         email = EmailMultiAlternatives(
#             subject=email_template.subject,
#             body=text_content,
#             from_email=sending_profile.smtp_from,
#             to=[recipient.email],
#         )
#         email.attach_alternative(html_content, "text/html")
#         for attachment in email_template.attachments:
#             email.attach_file(attachment)
#         email.send()

#         CampaignEvent.objects.create(
#             campaign=campaign,
#             user=recipient,
#             event_type='sent',
#         )