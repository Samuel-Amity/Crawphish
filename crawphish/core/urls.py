# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Campaigns
    path('campaigns/', views.CampaignListView.as_view(), name='campaigns'),
    path('campaigns/create/', views.CampaignCreateView.as_view(), name='campaign_create'),
    path('campaigns/edit/<int:pk>/', views.CampaignUpdateView.as_view(), name='campaign_edit'),
    path('campaigns/delete/<int:pk>/', views.CampaignDeleteView.as_view(), name='campaign_delete'),
    path('campaigns/copy/<int:pk>/', views.CampaignCopyView.as_view(), name='campaign_copy'),
    path('campaign-group-details/<int:group_id>/', views.get_campaign_group_details, name='campaign_group_details'),
    path('campaigns/detail/<int:pk>/', views.CampaignDetailView.as_view(), name='campaign_detail'),

    # Users & Groups
    path('users-groups/', views.GroupListView.as_view(), name='users_groups'),
    path('users-groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('users-groups/edit/<int:pk>/', views.GroupUpdateView.as_view(), name='group_edit'),
    path('users-groups/delete/<int:pk>/', views.GroupDeleteView.as_view(), name='group_delete'),

    # Email Templates
    path('email-templates/', views.EmailTemplateListView.as_view(), name='email_templates'),
    path('email-templates/create/', views.EmailTemplateCreateView.as_view(), name='email_template_create'),
    path('email-templates/edit/<int:pk>/', views.EmailTemplateUpdateView.as_view(), name='email_template_edit'),
    path('email-templates/delete/<int:pk>/', views.EmailTemplateDeleteView.as_view(), name='email_template_delete'),
    path('email-templates/copy/<int:pk>/', views.EmailTemplateCopyView.as_view(), name='email_template_copy'),
    path('email-templates/detail/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='email_template_detail'),
    # Landing Pages
    path('landing-pages/', views.LandingPageListView.as_view(), name='landing_pages'),
    path('landing-pages/create/', views.LandingPageCreateView.as_view(), name='landing_page_create'),
    path('landing-pages/<int:pk>/', views.LandingPageDetailView.as_view(), name='landing_page_detail'),
    path('landing-pages/<int:pk>/edit/', views.LandingPageUpdateView.as_view(), name='landing_page_edit'),
    path('landing-pages/<int:pk>/delete/', views.LandingPageDeleteView.as_view(), name='landing_page_delete'),
    path('landing-pages/<int:pk>/copy/', views.LandingPageCopyView.as_view(), name='landing_page_copy'),

    # Sending Profiles
    path('sending-profiles/', views.SendingProfileListView.as_view(), name='sending_profiles'),
    path('sending-profiles/<int:pk>/', views.SendingProfileDetailView.as_view(), name='sending_profile_detail'),
    path('sending-profiles/create/', views.SendingProfileCreateView.as_view(), name='sending_profile_create'),
    path('sending-profiles/edit/<int:pk>/', views.SendingProfileUpdateView.as_view(), name='sending_profile_edit'),
    path('sending-profiles/delete/<int:pk>/', views.SendingProfileDeleteView.as_view(), name='sending_profile_delete'),
    path('sending-profiles/copy/<int:pk>/', views.SendingProfileCopyView.as_view(), name='sending_profile_copy'),

    # Settings
    path('settings/', views.SettingsView.as_view(), name='settings'),

    # User Management (new)
    path('user-management/', views.UserListView.as_view(), name='user_management'),
    path('user-management/create/', views.UserCreateView.as_view(), name='user_create'),
    path('user-management/edit/<int:pk>/', views.UserUpdateView.as_view(), name='user_edit'),
    path('user-management/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users-groups/download-csv-template/', views.download_csv_template, name='download_csv_template'),

    # Webhooks (new)
    path('webhooks/', views.WebhookListView.as_view(), name='webhooks'),
    path('webhooks/create/', views.WebhookCreateView.as_view(), name='webhook_create'),
    path('webhooks/edit/<int:pk>/', views.WebhookUpdateView.as_view(), name='webhook_edit'),
    path('webhooks/delete/<int:pk>/', views.WebhookDeleteView.as_view(), name='webhook_delete'),

    # track email opens and link clicks
    path('track/open/<str:token>/', views.track_open, name='track_open'),
    path('track/click/<str:token>/', views.track_click, name='track_click'),
    path('landing/<str:token>/', views.landing_page_view, name='landing_page'),
] 