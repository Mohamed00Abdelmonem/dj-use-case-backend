from rest_framework import serializers
from .models import Integration, NAR
from apps.people.models import Developer
from apps.portfolio.models import UseCase
from apps.core.fields import SafePrimaryKeyRelatedField

class IntegrationSerializer(serializers.ModelSerializer):
    ownerId = serializers.CharField(source='owner_id', required=False, allow_blank=True, allow_null=True)
    dataObjects = serializers.CharField(source='data_objects', required=False, allow_blank=True, allow_null=True)
    useCaseIds = SafePrimaryKeyRelatedField(
        source='use_cases',
        queryset=UseCase.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'system', 'source', 'type', 'direction',
            'status', 'owner', 'ownerId', 'frequency', 'dataObjects', 'description',
            'useCaseIds'
        ]


class NarSerializer(serializers.ModelSerializer):
    requestDate = serializers.CharField(source='request_date', required=False, allow_blank=True, allow_null=True)
    endDate = serializers.CharField(source='end_date', required=False, allow_blank=True, allow_null=True)
    warningDays = serializers.IntegerField(source='warning_days', required=False)
    mailSubject = serializers.CharField(source='mail_subject', required=False, allow_blank=True, allow_null=True)
    approvalReference = serializers.CharField(source='approval_reference', required=False, allow_blank=True, allow_null=True)
    accessScope = serializers.CharField(source='access_scope', required=False, allow_blank=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    integrationIds = SafePrimaryKeyRelatedField(
        source='integration_ids',
        queryset=Integration.objects.all(),
        many=True,
        required=False
    )
    ownerIds = SafePrimaryKeyRelatedField(
        source='owner_ids',
        queryset=Developer.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = NAR
        fields = [
            'id', 'number', 'status', 'requestDate', 'endDate', 'warningDays',
            'mailSubject', 'requester', 'approvalReference', 'integrationIds',
            'ownerIds', 'accessScope', 'notes', 'createdAt', 'updatedAt'
        ]
