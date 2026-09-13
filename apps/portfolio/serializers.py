from rest_framework import serializers
from .models import Domain, Category, UseCase, Pipeline
from apps.people.models import Developer
from apps.gaps.models import Gap
from apps.integrations.models import Integration
from apps.core.fields import SafePrimaryKeyRelatedField

class UseCaseSerializer(serializers.ModelSerializer):
    categoryId = SafePrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    businessValue = serializers.CharField(source='business_value', required=False, allow_blank=True, allow_null=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    developerIds = SafePrimaryKeyRelatedField(
        source='developer_ids',
        queryset=Developer.objects.all(),
        many=True,
        required=False
    )
    integrationIds = SafePrimaryKeyRelatedField(
        source='integration_ids',
        queryset=Integration.objects.all(),
        many=True,
        required=False
    )
    gapIds = SafePrimaryKeyRelatedField(
        source='gap_ids',
        queryset=Gap.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = UseCase
        fields = [
            'id', 'categoryId', 'reference', 'name', 'description',
            'businessValue', 'outputs', 'status', 'notes', 'updatedAt',
            'developerIds', 'integrationIds', 'gapIds'
        ]


class CategorySerializer(serializers.ModelSerializer):
    domainId = SafePrimaryKeyRelatedField(
        source='domain',
        queryset=Domain.objects.all(),
        required=False,
        allow_null=True
    )
    useCases = UseCaseSerializer(source='use_cases', many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'domainId', 'name', 'description', 'order', 'useCases']


class DomainSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Domain
        fields = ['id', 'name', 'description', 'order', 'categories']


class PipelineSerializer(serializers.ModelSerializer):
    serverUrl = serializers.CharField(source='server_url', required=False, allow_blank=True, allow_null=True)
    repositoryUrl = serializers.CharField(source='repository_url', required=False, allow_blank=True, allow_null=True)
    pipelinePath = serializers.CharField(source='pipeline_path', required=False, allow_blank=True, allow_null=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    integrationIds = SafePrimaryKeyRelatedField(
        source='integration_ids',
        queryset=Integration.objects.all(),
        many=True,
        required=False
    )
    useCaseIds = SafePrimaryKeyRelatedField(
        source='use_case_ids',
        queryset=UseCase.objects.all(),
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
        model = Pipeline
        fields = [
            'id', 'name', 'uuid', 'type', 'status', 'server', 'serverUrl',
            'environment', 'schedule', 'timezone', 'repositoryUrl',
            'pipelinePath', 'integrationIds', 'useCaseIds', 'ownerIds',
            'blocks', 'description', 'notes', 'createdAt', 'updatedAt'
        ]
