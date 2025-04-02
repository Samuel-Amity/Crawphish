from django.contrib import admin
from .models import *

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'position', 'api_key', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')

class ExternalUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'position', 'created_at', 'updated_at')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('position',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count', 'modified_date')
    search_fields = ('name',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'

class ClickerGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class SubmitterGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'envelope_sender', 'difficulty', 'modified_date')
    search_fields = ('name', 'subject')
    list_filter = ('difficulty',)

class LandingPageAdmin(admin.ModelAdmin):
    list_display = ('name', 'capture_submitted_data', 'modified_date')
    search_fields = ('name',)

class SendingProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'interface_type', 'smtp_from', 'host', 'port', 'modified_date')
    search_fields = ('name', 'smtp_from', 'host')

class CampaignGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_template', 'landing_page', 'sending_profile', 'campaign_count')
    search_fields = ('name',)

    def campaign_count(self, obj):
        return obj.campaign_set.count()
    campaign_count.short_description = 'Campaign Count'

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'launch_date', 'frequency', 'send_to_all_users', 'status')
    search_fields = ('name',)
    list_filter = ('status', 'frequency')

class CampaignEventAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'event_type', 'timestamp')
    search_fields = ('campaign__name', 'user__email', 'event_type')
    list_filter = ('event_type',)

class WebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'created_by', 'created_at', 'modified_at')
    search_fields = ('name', 'url')

admin.site.register(User, UserAdmin)
admin.site.register(ExternalUser, ExternalUserAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(ClickerGroup, ClickerGroupAdmin)
admin.site.register(SubmitterGroup, SubmitterGroupAdmin)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(LandingPage, LandingPageAdmin)
admin.site.register(SendingProfile, SendingProfileAdmin)
admin.site.register(CampaignGroup, CampaignGroupAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(CampaignEvent, CampaignEventAdmin)
admin.site.register(Webhook, WebhookAdmin)
admin.site.register(Attachment)
