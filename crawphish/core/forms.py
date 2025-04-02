from django import forms
from .models import *

class CampaignForm(forms.ModelForm):
    campaign_group = forms.ModelChoiceField(
        queryset=CampaignGroup.objects.all(), required=False, empty_label="Custom"
    )
    class Meta:
        model = Campaign
        fields = '__all__'
        widgets = {
            'launch_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class GroupForm(forms.ModelForm):
    bulk_import_file = forms.FileField(required=False, label="Bulk Import Users")

    class Meta:
        model = Group
        fields = ['name']  # Only include the name field; members are handled separately

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class EmailTemplateForm(forms.ModelForm):
    attachment = forms.FileField(
        required=False,
        widget=forms.FileInput(),
        label="Add Attachment"
    )

    class Meta:
        model = EmailTemplate
        fields = ['name', 'envelope_sender', 'subject', 'add_tracking_image', 'difficulty', 'html_content', 'plain_content']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter template name'}),
            'envelope_sender': forms.TextInput(attrs={'placeholder': 'First Last <test@example.com>'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Email Subject'}),
        }

    plain_content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10}), required=False)
    html_content = forms.CharField(widget=forms.Textarea(attrs={'class': 'tinymce form-control', 'rows': 10}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()
        if not self.instance.pk:
            self.fields['html_content'].initial = """<html>
<head>
    <title></title>
</head>
<body>
</body>
</html>"""

class LandingPageForm(forms.ModelForm):
    html_content = forms.CharField(widget=forms.Textarea(attrs={'class': 'tinymce form-control', 'rows': 10}))

    class Meta:
        model = LandingPage
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput):
                existing_classes = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing_classes + ' form-control').strip()
        self.fields['capture_submitted_data'].widget.attrs.pop('class', None)
        self.fields['capture_submitted_data'].widget.attrs.update({'class': 'form-check-input'})

class SendingProfileForm(forms.ModelForm):
    class Meta:
        model = SendingProfile
        fields = ['name', 'interface_type', 'smtp_from', 'host', 'port', 'username', 'password', 'ignore_cert_errors', 'email_headers']
        widgets = {
            'email_headers': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['password'].required = False
        self.fields['email_headers'].required = False
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

