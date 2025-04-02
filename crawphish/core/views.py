# Standard Library Imports
import os
import csv
# Django Core and Utility Imports
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.signing import Signer, BadSignature
# Class-Based Views and Mixins
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
# Application-Specific Imports
from .models import *
from .forms import *

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

# Dashboard
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        campaigns = Campaign.objects.all().order_by('-launch_date')
        metrics = {
            'total_campaigns': campaigns.count(),
            'emails_sent': CampaignEvent.objects.filter(event_type='sent').count(),
            'emails_opened': CampaignEvent.objects.filter(event_type='opened').count(),
            'links_clicked': CampaignEvent.objects.filter(event_type='clicked').count(),
            'data_submitted': CampaignEvent.objects.filter(event_type='submitted').count(),
            'emails_reported': CampaignEvent.objects.filter(event_type='reported').count(),
        }
        context['campaigns'] = campaigns
        context['metrics'] = metrics
        
        # Add per-campaign stats
        campaign_stats = []
        for campaign in campaigns:
            stats = {
                'name': campaign.name,
                'sent': campaign.events.filter(event_type='sent').count(),
                'opened': campaign.events.filter(event_type='opened').count(),
                'clicked': campaign.events.filter(event_type='clicked').count(),
                'submitted': campaign.events.filter(event_type='submitted').count(),
            }
            campaign_stats.append(stats)
        context['campaign_stats'] = campaign_stats
        return context

# Campaigns

class CampaignListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'core/campaigns.html'
    context_object_name = 'campaigns'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_campaigns'] = Campaign.objects.filter(status='active')
        context['archived_campaigns'] = Campaign.objects.filter(status='archived')
        return context

class CampaignCreateView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'core/campaign_create.html'
    success_url = reverse_lazy('core:campaigns')

class CampaignUpdateView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'core/campaign_edit.html'
    success_url = reverse_lazy('core:campaigns')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['campaign'] = self.object
        return context

class CampaignDeleteView(LoginRequiredMixin, DeleteView):
    model = Campaign
    template_name = 'core/campaigns.html'  # Redirects back to list, no separate confirmation page
    success_url = reverse_lazy('core:campaigns')

class CampaignCopyView(LoginRequiredMixin, CreateView):
    model = Campaign
    form_class = CampaignForm
    template_name = 'core/campaign_create.html'  # Reuse create template for copy
    success_url = reverse_lazy('core:campaigns')

    def get_initial(self):
        campaign = self.get_object()
        initial = {
            'name': f"Copy of {campaign.name}",
            'url': campaign.url,
            'launch_date': campaign.launch_date,
            'end_date': campaign.end_date,
            'sending_profile': campaign.sending_profile,
            'status': campaign.status,
            'send_to_all_users': campaign.send_to_all_users,
            'frequency': campaign.frequency,
            'sending_period_type': campaign.sending_period_type,
            'sending_period_days': campaign.sending_period_days,
            'track_activity_duration': campaign.track_activity_duration,
            'track_replied_emails': campaign.track_replied_emails,
            'send_report_after_end': campaign.send_report_after_end,
            'hide_from_dashboard': campaign.hide_from_dashboard,
        }
        return initial

    def get_object(self):
        return Campaign.objects.get(pk=self.kwargs['pk'])

    def form_valid(self, form):
        self.object = form.save()
        original_campaign = self.get_object()
        self.object.groups.set(original_campaign.groups.all())
        self.object.email_templates.set(original_campaign.email_templates.all())
        self.object.landing_pages.set(original_campaign.landing_pages.all())
        self.object.clicker_groups.set(original_campaign.clicker_groups.all())
        self.object.submitter_groups.set(original_campaign.submitter_groups.all())
        self.object.save()
        return super().form_valid(form)

class CampaignDetailView(LoginRequiredMixin, DetailView):
    model = Campaign
    template_name = 'core/campaign_detail.html'
    context_object_name = 'campaign'

def get_campaign_group_details(request, group_id):
    group = get_object_or_404(CampaignGroup, id=group_id)
    return JsonResponse({
        'email_template': group.email_template.id if group.email_template else None,
        'landing_page': group.landing_page.id if group.landing_page else None,
        'sending_profile': group.sending_profile.id if group.sending_profile else None,
    })

# Users & Groups

class GroupListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'core/users_groups.html'
    context_object_name = 'groups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GroupForm()
        return context

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'core/users_groups.html'
    success_url = reverse_lazy('core:users_groups')

    def form_valid(self, form):
        self.object = form.save()  # Set self.object
        # Check if table data (first_name[], last_name[], etc.) is provided
        emails = self.request.POST.getlist('email[]')
        if emails:  # Prioritize table data
            first_names = self.request.POST.getlist('first_name[]')
            last_names = self.request.POST.getlist('last_name[]')
            positions = self.request.POST.getlist('position[]')
            for i in range(len(emails)):
                if emails[i]:
                    external_user, created = ExternalUser.objects.update_or_create(
                        email=emails[i],
                        defaults={
                            'first_name': first_names[i],
                            'last_name': last_names[i],
                            'position': positions[i]
                        }
                    )
                    self.object.members.add(external_user)
        elif 'bulk_import_file' in self.request.FILES:  # Fallback to CSV if no table data
            csv_file = self.request.FILES['bulk_import_file']
            from io import TextIOWrapper
            reader = csv.DictReader(TextIOWrapper(csv_file, 'utf-8'))
            for row in reader:
                external_user, created = ExternalUser.objects.update_or_create(
                    email=row['email'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'position': row.get('position', '')
                    }
                )
                self.object.members.add(external_user)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Group created successfully',
                'redirect_url': self.get_success_url()
            }, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)
    
def download_csv_template(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="group_members_template.csv"'
    writer = csv.writer(response)
    writer.writerow(['first_name', 'last_name', 'email', 'position'])
    return response

class GroupUpdateView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'core/users_groups.html'
    success_url = reverse_lazy('core:users_groups')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.get_object()
        context['members'] = self.get_object().members.all()
        return context

    def form_valid(self, form):
        self.object = form.save()  # Set self.object
        self.object.members.clear()
        # Check if table data (first_name[], last_name[], etc.) is provided
        emails = self.request.POST.getlist('email[]')
        if emails:  # Prioritize table data
            first_names = self.request.POST.getlist('first_name[]')
            last_names = self.request.POST.getlist('last_name[]')
            positions = self.request.POST.getlist('position[]')
            for i in range(len(emails)):
                if emails[i]:
                    external_user, created = ExternalUser.objects.update_or_create(
                        email=emails[i],
                        defaults={
                            'first_name': first_names[i],
                            'last_name': last_names[i],
                            'position': positions[i]
                        }
                    )
                    self.object.members.add(external_user)
        elif 'bulk_import_file' in self.request.FILES:  # Fallback to CSV if no table data
            csv_file = self.request.FILES['bulk_import_file']
            from io import TextIOWrapper
            reader = csv.DictReader(TextIOWrapper(csv_file, 'utf-8'))
            for row in reader:
                external_user, created = ExternalUser.objects.update_or_create(
                    email=row['email'],
                    defaults={
                        'first_name': row['first_name'],
                        'last_name': row['last_name'],
                        'position': row.get('position', '')
                    }
                )
                self.object.members.add(external_user)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Group updated successfully',
                'redirect_url': self.get_success_url()
            }, status=200)
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)
    
class GroupDeleteView(LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'core/group_confirm_delete.html'
    success_url = reverse_lazy('core:users_groups')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Group deleted successfully',
                'redirect_url': self.get_success_url()
            }, status=200)
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'GET request not allowed for deletion'
            }, status=405)
        return super().get(request, *args, **kwargs)

# Email Templates

class EmailTemplateListView(LoginRequiredMixin, ListView):
    model = EmailTemplate
    template_name = 'core/email_templates.html'
    context_object_name = 'email_templates'

class EmailTemplateCreateView(LoginRequiredMixin, CreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'core/email_template_create.html'
    success_url = reverse_lazy('core:email_templates')

    def form_valid(self, form):
        email_template = form.save(commit=False)
        email_template.plain_content = form.cleaned_data['plain_content']
        email_template.html_content = form.cleaned_data['html_content']
        email_template.save()
        attachment = self.request.FILES.get('attachment')
        if attachment:
            Attachment.objects.create(email_template=email_template, file=attachment)
        return super().form_valid(form)

class EmailTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'core/email_template_edit.html'
    success_url = reverse_lazy('core:email_templates')

    def form_valid(self, form):
        email_template = form.save(commit=False)
        email_template.plain_content = form.cleaned_data['plain_content']
        email_template.html_content = form.cleaned_data['html_content']
        email_template.save()
        attachment = self.request.FILES.get('attachment')
        if attachment:
            # Handle updating or adding attachments as needed
            Attachment.objects.create(email_template=email_template, file=attachment)
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['plain_content'] = self.get_object().plain_content
        initial['html_content'] = self.get_object().html_content
        return initial

class EmailTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = EmailTemplate
    template_name = 'core/email_template_delete.html'
    success_url = reverse_lazy('core:email_templates')

class EmailTemplateCopyView(LoginRequiredMixin, CreateView):
    model = EmailTemplate
    form_class = EmailTemplateForm
    template_name = 'core/email_template_create.html'  # Reuse create template
    success_url = reverse_lazy('core:email_templates')

    def get_initial(self):
        template = get_object_or_404(EmailTemplate, pk=self.kwargs['pk'])
        return {
            'name': f"Copy of {template.name}",
            'plain_content': template.plain_content,
            'envelope_sender': template.envelope_sender,
            'subject': template.subject,
            'html_content': template.html_content,
            'add_tracking_image': template.add_tracking_image,
        }

    def form_valid(self, form):
        # Debug: Print or log the html_content to ensure it's coming through
        html_content = self.request.POST.get('html_content', '')
        print('DEBUG: html_content submitted:', html_content)
        return super().form_valid(form)


class EmailTemplateDetailView(LoginRequiredMixin, DetailView):
    model = EmailTemplate
    template_name = 'core/email_template_detail.html'
    context_object_name = 'template'

# Landing Pages

class LandingPageListView(LoginRequiredMixin, ListView):
    model = LandingPage
    template_name = 'core/landing_pages.html'
    context_object_name = 'landing_pages'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class LandingPageCreateView(LoginRequiredMixin, CreateView):
    model = LandingPage
    form_class = LandingPageForm
    template_name = 'core/landing_page_create.html'
    success_url = reverse_lazy('core:landing_pages')

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class LandingPageDetailView(LoginRequiredMixin, DetailView):
    model = LandingPage
    template_name = 'core/landing_page_detail.html'
    context_object_name = 'landing_page'

class LandingPageUpdateView(LoginRequiredMixin, UpdateView):
    model = LandingPage
    form_class = LandingPageForm
    template_name = 'core/landing_page_edit.html'
    success_url = reverse_lazy('core:landing_pages')

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class LandingPageDeleteView(LoginRequiredMixin, DeleteView):
    model = LandingPage
    template_name = 'core/landing_page_confirm_delete.html' # You might not need this template anymore
    success_url = reverse_lazy('core:landing_pages')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())

class LandingPageCopyView(LoginRequiredMixin, CreateView):
    model = LandingPage
    form_class = LandingPageForm
    template_name = 'core/landing_page_create.html'
    success_url = reverse_lazy('core:landing_pages')

    def get_initial(self):
        try:
            page = LandingPage.objects.get(pk=self.kwargs['pk'])
            return {
                'name': f"Copy of {page.name}",
                'html_content': page.html_content,
                'capture_submitted_data': page.capture_submitted_data,
            }
        except LandingPage.DoesNotExist:
            return {}

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
    
# Sending Profiles  

class SendingProfileListView(LoginRequiredMixin, ListView):
    model = SendingProfile
    template_name = 'core/sending_profiles.html'
    context_object_name = 'sending_profiles'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SendingProfileForm()
        return context

class SendingProfileDetailView(LoginRequiredMixin, DetailView):
    model = SendingProfile
    template_name = 'core/sending_profile_detail.html'
    context_object_name = 'profile'

class SendingProfileCreateView(LoginRequiredMixin, CreateView):
    model = SendingProfile
    form_class = SendingProfileForm
    template_name = 'core/sending_profile_create.html'
    success_url = reverse_lazy('core:sending_profiles')

    def form_valid(self, form):
        return super().form_valid(form)

class SendingProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = SendingProfile
    form_class = SendingProfileForm
    template_name = 'core/sending_profile_edit.html'
    success_url = reverse_lazy('core:sending_profiles')

    def form_valid(self, form):
        return super().form_valid(form)

class SendingProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = SendingProfile
    template_name = 'core/sending_profile_confirm_delete.html'  # Optional, but we'll keep it for consistency
    success_url = reverse_lazy('core:sending_profiles')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return redirect(self.get_success_url())

class SendingProfileCopyView(LoginRequiredMixin, CreateView):
    model = SendingProfile
    form_class = SendingProfileForm
    template_name = 'core/sending_profile_create.html'  # Reuse create template
    success_url = reverse_lazy('core:sending_profiles')

    def get_initial(self):
        try:
            profile = SendingProfile.objects.get(pk=self.kwargs['pk'])
            return {
                'name': f"Copy of {profile.name}",
                'interface_type': profile.interface_type,
                'smtp_from': profile.smtp_from,
                'host': profile.host,
                'port': profile.port,
                'username': profile.username,
                'password': profile.password,
                'ignore_cert_errors': profile.ignore_cert_errors,
                'email_headers': profile.email_headers,
            }
        except SendingProfile.DoesNotExist:
            return {}

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

# Settings

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'core/settings.html'

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')

        user = request.user
        if not user.check_password(password):
            return JsonResponse({
                'success': False,
                'errors': {'password': 'Current password is incorrect.'}
            }, status=400)

        if username:
            user.username = username
        if new_password:
            user.set_password(new_password)
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Settings updated successfully'
        })

# User Management

class UserListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'core/user_management.html'
    context_object_name = 'users'

class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'position', 'is_superuser']
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_management')

    def form_valid(self, form):
        user = form.save(commit=False)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'User created successfully. Temporary password: {password}',
                'redirect_url': self.get_success_url()
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)

class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    fields = ['username', 'email', 'first_name', 'last_name', 'position', 'is_superuser']
    template_name = 'core/user_form.html'
    success_url = reverse_lazy('core:user_management')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'User updated successfully',
                'redirect_url': self.get_success_url()
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)

class UserDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'core/user_confirm_delete.html'
    success_url = reverse_lazy('core:user_management')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object == self.request.user:
            return JsonResponse({
                'success': False,
                'message': 'You cannot delete your own account.'
            }, status=400)
        self.object.delete()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'User deleted successfully',
                'redirect_url': self.get_success_url()
            })
        return super().delete(request, *args, **kwargs)

# Webhooks

class WebhookListView(LoginRequiredMixin, ListView):
    model = Webhook
    template_name = 'core/webhooks.html'
    context_object_name = 'webhooks'

    def get_queryset(self):
        return Webhook.objects.filter(created_by=self.request.user)

class WebhookCreateView(LoginRequiredMixin, CreateView):
    model = Webhook
    fields = ['name', 'url', 'events']
    template_name = 'core/webhook_form.html'
    success_url = reverse_lazy('core:webhooks')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Webhook created successfully',
                'redirect_url': self.get_success_url()
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)

class WebhookUpdateView(LoginRequiredMixin, UpdateView):
    model = Webhook
    fields = ['name', 'url', 'events']
    template_name = 'core/webhook_form.html'
    success_url = reverse_lazy('core:webhooks')

    def get_queryset(self):
        return Webhook.objects.filter(created_by=self.request.user)

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Webhook updated successfully',
                'redirect_url': self.get_success_url()
            })
        return response

    def form_invalid(self, form):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)

class WebhookDeleteView(LoginRequiredMixin, DeleteView):
    model = Webhook
    template_name = 'core/webhook_confirm_delete.html'
    success_url = reverse_lazy('core:webhooks')

    def get_queryset(self):
        return Webhook.objects.filter(created_by=self.request.user)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Webhook deleted successfully',
                'redirect_url': self.get_success_url()
            })
        return super().delete(request, *args, **kwargs)
    
# Tracking

def track_open(request, token):
    signer = Signer()
    try:
        campaign_id, recipient_id = map(int, signer.unsign(token).split(':'))
        campaign = Campaign.objects.get(id=campaign_id)
        recipient = ExternalUser.objects.get(id=recipient_id)
        CampaignEvent.objects.create(
            campaign=campaign,
            user=recipient,
            event_type='opened',
        )
        pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        return HttpResponse(pixel, content_type='image/gif')
    except (BadSignature, ValueError, Campaign.DoesNotExist, ExternalUser.DoesNotExist):
        return HttpResponse(status=404)

def track_click(request, token):
    signer = Signer()
    try:
        campaign_id, recipient_id = map(int, signer.unsign(token).split(':'))
        campaign = Campaign.objects.get(id=campaign_id)
        recipient = ExternalUser.objects.get(id=recipient_id)
        CampaignEvent.objects.create(
            campaign=campaign,
            user=recipient,
            event_type='clicked',
        )
        return redirect(f"/landing/{token}/")
    except (BadSignature, ValueError, Campaign.DoesNotExist, ExternalUser.DoesNotExist):
        return HttpResponse(status=404)

def landing_page_view(request, token):
    signer = Signer()
    try:
        campaign_id, recipient_id = map(int, signer.unsign(token).split(':'))
        campaign = Campaign.objects.get(id=campaign_id)
        recipient = ExternalUser.objects.get(id=recipient_id)
        landing_page = campaign.landing_page

        if request.method == 'POST' and landing_page.capture_submitted_data:
            form_data = request.POST.dict()
            CampaignEvent.objects.create(
                campaign=campaign,
                user=recipient,
                event_type='submitted',
                details=form_data,
            )
            return HttpResponse("Thank you for your submission!", content_type="text/plain")

        return HttpResponse(landing_page.html_content, content_type="text/html")
    except (BadSignature, ValueError, Campaign.DoesNotExist, ExternalUser.DoesNotExist):
        return HttpResponse(status=404)








