from django.db import models
from django.utils.translation import ugettext as _
from django_extensions.db.fields import ModificationDateTimeField
from django_extensions.db.models import TimeStampedModel


class DeletedModel(TimeStampedModel):
    """
    Deleted model, flags when an instance is deleted.
    """
    
    deleted = ModificationDateTimeField(_('deleted')) 
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        abstract = True


class PhoneNumberModel(models.Model):
    """
    Phone number model, keeps a raw input version and a clean version (only has digits).
    """
    
    #TODO: check possibilities for integration of 
    # - http://pypi.python.org/pypi/phonenumbers and/or
    # - https://github.com/stefanfoulis/django-phonenumber-field
    
    PHONE_TYPE_CHOICES = (
        ('work', _('Work')),
        ('mobile', _('Mobile')),
        ('home', _('Home')),
        ('fax_home', _('Fax (home)')),
        ('fax_work', _('Fax (work)')),
        ('data', _('Data')),
        ('pager', _('Pager')),
        ('other', _('Other')),
    )
    
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    PHONE_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )
    
    raw_input = models.CharField(max_length=40, verbose_name=_('phone number'))
    number = models.CharField(max_length=40)
    type = models.CharField(max_length=15, choices=PHONE_TYPE_CHOICES, default='work', 
                            verbose_name=_('type'))
    other_type = models.CharField(max_length=15, blank=True, null=True) # used in combination with type='other'
    status = models.IntegerField(max_length=10, choices=PHONE_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    
    def __unicode__(self):
        return self.number
    
    def save(self):
        # Save raw input
        self.number = filter(type(self.raw_input).isdigit, self.raw_input)
        
        super(PhoneNumberModel, self).save()
    
    class Meta:
        verbose_name = _('phone number')
        verbose_name_plural = _('phone numbers')


class SocialMediaModel(models.Model):
    """
    Social media model, default supporting a few well known social media but has support for 
    custom input (other_name).
    """
    
    SOCIAL_NAME_CHOICES = (
        ('facebook', _('Facebook')),
        ('twitter', _('Twitter')),
        ('linkedin', _('LinkedIn')),
        ('googleplus', _('Google+')),
        ('qzone', _('Qzone')),
        ('orkut', _('Orkut')),
        ('other', _('Other')),
    )
    
    name = models.CharField(max_length=30,choices=SOCIAL_NAME_CHOICES, verbose_name=_('name'))
    other_name = models.CharField(max_length=30, blank=True, null=True) # used in combination with name='other'
    username = models.CharField(max_length=100, blank=True, verbose_name=_('username'))
    profile_url = models.URLField(verbose_name=_('profile link'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('social media')
        verbose_name_plural = _('social media')


class AddressModel(models.Model):
    """
    Address model, has most default fields for an address and fixed preset values for type. In
    the view layer options are limited for different models. For example: options for an address
    for an account excludes 'home' as options for an address for a contact exclude 'visiting'.
    """
    
    ADDRESS_TYPE_CHOICES = (
        ('visiting', _('Visiting address')),
        ('billing', _('Billing address')),
        ('mailing', _('Mailing address')),
        ('shipping', _('Shipping address')),
        ('home', _('Home address')),
        ('other', _('Other')),
    )
    
    street = models.CharField(max_length=255, verbose_name=_('street'), blank=True)
    street_number = models.SmallIntegerField(verbose_name=_('street number'), blank=True, null=True)
    complement = models.CharField(max_length=10, verbose_name=_('complement'), blank=True)
    postal_code = models.CharField(max_length=10, verbose_name=_('postal code'), blank=True)
    city = models.CharField(max_length=100, verbose_name=_('city'), blank=True)
    state_province = models.CharField(max_length=50, verbose_name=_('state/province'), blank=True)
    # TODO: maybe try setting a default based on account/user preferences for country
    country = models.CharField(max_length=200, verbose_name=_('country'), blank=True)
    type = models.CharField(max_length=20, choices=ADDRESS_TYPE_CHOICES, verbose_name=_('type'))

    def __unicode__(self):
        return u'%s %s' % (self.postal_code, self.street_number)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class EmailAddressModel(models.Model):
    """
    Email address model, it's possible to set an email address as primary address as a model can 
    own multiple email addresses.
    """
    
    INACTIVE_STATUS, ACTIVE_STATUS = range(2)
    EMAIL_STATUS_CHOICES = (
        (INACTIVE_STATUS, _('Inactive')),
        (ACTIVE_STATUS, _('Active')),
    )
    
    email_address = models.EmailField(max_length=255, verbose_name=_('e-mail address'))
    is_primary = models.BooleanField(default=False, verbose_name=_('primary e-mail'))
    status = models.IntegerField(max_length=50, choices=EMAIL_STATUS_CHOICES, default=ACTIVE_STATUS,
                                 verbose_name=_('status'))
    
    def __unicode__(self):
        return self.email_address

    class Meta:
        verbose_name = _('e-mail address')
        verbose_name_plural = _('e-mail addresses')


class NoteModel(models.Model):
    """
    Note model, simple text fields to store text about another model for everyone to see.
    """
    
    note = models.TextField(verbose_name=_('note'))
    
    def __unicode__(self):
        return self.note

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')


class CommonModel(DeletedModel):
    """
    Common model to make it possible to easily define relations to other models.
    """
    
    phone_numbers = models.ManyToManyField(PhoneNumberModel, 
                                           verbose_name=_('list of phone numbers'))
    social_media = models.ManyToManyField(SocialMediaModel, verbose_name=_('list of social media'))
    addresses = models.ManyToManyField(AddressModel, verbose_name=_('list of addresses'))
    email_addresses = models.ManyToManyField(EmailAddressModel,
                                             verbose_name=_('list of e-mail addresses'))
    notes = models.ManyToManyField(NoteModel, verbose_name=_('list of notes'))
    
    class Meta:
        abstract = True