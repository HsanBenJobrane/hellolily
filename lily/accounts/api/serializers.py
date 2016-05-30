from lily.api.nested.mixins import RelatedSerializerMixin
from lily.api.nested.serializers import WritableNestedSerializer
from lily.contacts.models import Contact
from lily.utils.functions import clean_website
from rest_framework import serializers

from lily.api.serializers import ContentTypeSerializer
from lily.socialmedia.api.serializers import RelatedSocialMediaSerializer
from lily.users.api.serializers import RelatedLilyUserSerializer
from lily.utils.api.serializers import (RelatedAddressSerializer, RelatedEmailAddressSerializer,
                                        RelatedPhoneNumberSerializer, RelatedTagSerializer)

from ..models import Account, Website, AccountStatus
from .validators import DuplicateAccountName, HostnameValidator


class WebsiteSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=True, max_length=255, validators=[HostnameValidator()])

    def validate_website(self, value):
        return clean_website(value)

    class Meta:
        model = Website
        fields = (
            'id',
            'is_primary',
            'website',
        )


class RelatedWebsiteSerializer(RelatedSerializerMixin, WebsiteSerializer):
    pass


class ContactForAccountSerializer(serializers.ModelSerializer):
    """
    Serializer for Contact model related to Accounts.
    This serializer is a small subset for the related Contact model.
    """
    class Meta:
        model = Contact
        fields = (
            'id',
            'first_name',
            'full_name',
            'gender',
            'last_name',
            'preposition',
            'salutation',
        )


class AccountStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for account status model.
    """
    class Meta:
        model = AccountStatus
        fields = (
            'id',
            'name',
            'position',
        )


class RelatedAccountStatusSerializer(RelatedSerializerMixin, AccountStatusSerializer):
    pass


class AccountSerializer(WritableNestedSerializer):
    """
    Serializer for the account model.
    """
    # Read only fields.
    content_type = ContentTypeSerializer(read_only=True)
    flatname = serializers.CharField(read_only=True)
    contacts = ContactForAccountSerializer(many=True, read_only=True)

    # Related fields
    addresses = RelatedAddressSerializer(many=True, required=False, create_only=True)
    assigned_to = RelatedLilyUserSerializer(required=False, assign_only=True)
    email_addresses = RelatedEmailAddressSerializer(many=True, required=False, create_only=True)
    phone_numbers = RelatedPhoneNumberSerializer(many=True, required=False, create_only=True)
    social_media = RelatedSocialMediaSerializer(many=True, required=False, create_only=True)
    status = RelatedAccountStatusSerializer(assign_only=True)
    tags = RelatedTagSerializer(many=True, required=False, create_only=True)
    websites = RelatedWebsiteSerializer(many=True, required=False, create_only=True)

    # Custom fields.
    name = serializers.CharField(validators=[DuplicateAccountName()])

    def create(self, validated_data):
        """
        Reverse foreign key relations don't work yet with
        WritableNestedSerializer, so we manually create them.

        Args:
            validated_data (dict): The validated deserialized data.
        """
        websites = validated_data.pop('websites', {})
        account = super(AccountSerializer, self).create(validated_data)

        for website in websites:
            website['account'] = account
            Website.objects.create(**website)

        return account

    def update(self, instance, validated_data):
        """
        Reverse foreign key relations don't work yet with
        WritableNestedSerializer, so we manually update them.

        Args:
            validated_data (dict): The validated deserialized data.
        """
        websites_data = validated_data.pop('websites', {})
        account = super(AccountSerializer, self).update(instance, validated_data)
        if self.partial:
            # For a PATCH we only apply a delta to existing resources.
            for website in websites_data:
                if 'id' in website:
                    Website.objects.filter(pk=website.pop('id')).update(**website)
                else:
                    website['account'] = account
                    Website.objects.create(**website)
        else:
            # For a PUT we replace the whole resource.
            account.websites.all().delete()
            for website in websites_data:
                website['account'] = account
                Website.objects.create(**website)

        return account

    class Meta:
        model = Account
        fields = (
            'addresses',
            'assigned_to',
            'bankaccountnumber',
            'bic',
            'cocnumber',
            'contacts',
            'content_type',
            'customer_id',
            'description',
            'email_addresses',
            'flatname',
            'iban',
            'legalentity',
            # 'logo',
            'id',
            'modified',
            'name',
            'phone_numbers',
            'social_media',
            'status',
            'tags',
            'taxnumber',
            'websites',
        )


class RelatedAccountSerializer(RelatedSerializerMixin, AccountSerializer):
    """
    Serializer for the account model when used as a relation.
    """
    class Meta:
        model = Account
        fields = (  # No related fields in this serializer.
            'id',
            'bankaccountnumber',
            'bic',
            'cocnumber',
            'company_size',
            'created',
            'customer_id',
            'description',
            'flatname',
            'iban',
            'legalentity',
            'modified',
            'name',
            'status',
            'taxnumber',
            'email_addresses',
            'phone_numbers',
            'addresses',
        )
