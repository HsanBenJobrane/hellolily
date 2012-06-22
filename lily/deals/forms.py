from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext as _

from lily.accounts.models import Account
from lily.deals.models import Deal
from lily.tenant.middleware import get_current_user
from lily.users.models import CustomUser


class AddDealForm(ModelForm):
    """
    Form for adding a deal which includes all fields available.
    """
    account = forms.ModelChoiceField(queryset=Account.objects.none(), empty_label=_('Select an account'), 
        widget=forms.Select({
             'class': 'chzn-select tabbable',
    }))
    
    assigned_to = forms.ModelChoiceField(queryset=CustomUser.objects.none(), empty_label=None, 
        widget=forms.Select({
             'class': 'chzn-select-no-search tabbable',
    }))
    
    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to make accounts available as assignees.
        """
        super(AddDealForm, self).__init__(*args, **kwargs)
        
        # Provide filtered query set
        self.fields['account'].queryset = Account.objects.all()
        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using CustomUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the CustomUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        #
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()
        
    class Meta:
        model = Deal
        exclude = ('closed_date', 'tenant')
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Name'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search tabbable',
            }),
            'amount': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Amount'),
            }),
            'expected_closing_date': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('YYYY-MM-DD'),
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search tabbable',
            }),
        }


class EditDealForm(ModelForm):
    """
    Form for editing an existing deal which includes all fields available.
    """
    account = forms.ModelChoiceField(queryset=Account.objects.none(), empty_label=_('Select an account'), 
        widget=forms.Select({
             'class': 'chzn-select tabbable',
    }))
    
    assigned_to = forms.ModelChoiceField(queryset=CustomUser.objects.none(), empty_label=None, 
        widget=forms.Select({
             'class': 'chzn-select-no-search tabbable',
    }))
    
    def __init__(self, *args, **kwargs):
        """
        Overloading super().__init__() to make accounts available as assignees.
        """
        super(EditDealForm, self).__init__(*args, **kwargs)
        
        # Provide filtered query set
        self.fields['account'].queryset = Account.objects.all()
        # FIXME: WORKAROUND FOR TENANT FILTER.
        # An error will occur when using CustomUser.objects.all(), most likely because
        # the foreign key to contact (and maybe account) is filtered and executed before
        # the filter for the CustomUser. This way it's possible contacts (and maybe accounts)
        # won't be found for a user. But since it's a required field, an exception is raised.
        #
        self.fields['assigned_to'].queryset = CustomUser.objects.filter(tenant=get_current_user().tenant)
        self.fields['assigned_to'].initial = get_current_user()
        
    class Meta:
        model = Deal
        exclude = ('closed_date', 'tenant')
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Name'),
            }),
            'description': forms.Textarea(attrs={
                'cols': '60',
                'rows': '3',
                'class': 'tabbable',
                'placeholder': _('Description'),
            }),
            'currency': forms.Select(attrs={
                'class': 'chzn-select-no-search tabbable',
            }),
            'amount': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('Amount'),
            }),
            'expected_closing_date': forms.TextInput(attrs={
                'class': 'mws-textinput tabbable',
                'placeholder': _('YYYY-MM-DD'),
            }),
            'stage': forms.Select(attrs={
                'class': 'chzn-select-no-search tabbable',
            }),
        }