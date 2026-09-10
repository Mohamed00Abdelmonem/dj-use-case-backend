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
