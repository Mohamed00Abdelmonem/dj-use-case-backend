from rest_framework import serializers
from .models import Domain, Category, UseCase
from apps.people.models import Developer
from apps.gaps.models import Gap
from apps.integrations.models import Integration

class UseCaseSerializer(serializers.ModelSerializer):
    categoryId = serializers.PrimaryKeyRelatedField(
        source='category',
        queryset=Category.objects.all(),
        required=False
    )
    businessValue = serializers.CharField(source='business_value', required=False, allow_blank=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    developerIds = serializers.PrimaryKeyRelatedField(
        source='developer_ids',
        queryset=Developer.objects.all(),
        many=True,
        required=False
    )
    integrationIds = serializers.PrimaryKeyRelatedField(
        source='integration_ids',
        queryset=Integration.objects.all(),
        many=True,
        required=False
    )
    gapIds = serializers.PrimaryKeyRelatedField(
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
    domainId = serializers.PrimaryKeyRelatedField(
        source='domain',
        queryset=Domain.objects.all(),
        required=False
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


from .models import Pipeline

class PipelineSerializer(serializers.ModelSerializer):
    serverUrl = serializers.CharField(source='server_url', required=False, allow_blank=True)
    repositoryUrl = serializers.CharField(source='repository_url', required=False, allow_blank=True)
    pipelinePath = serializers.CharField(source='pipeline_path', required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    integrationIds = serializers.PrimaryKeyRelatedField(
        source='integration_ids',
        queryset=Integration.objects.all(),
        many=True,
        required=False
    )
    useCaseIds = serializers.PrimaryKeyRelatedField(
        source='use_case_ids',
        queryset=UseCase.objects.all(),
        many=True,
        required=False
    )
    ownerIds = serializers.PrimaryKeyRelatedField(
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
