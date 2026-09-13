from rest_framework import serializers
from .models import GapClassification, Gap
from apps.people.models import Developer
from apps.portfolio.models import UseCase
from apps.core.fields import SafePrimaryKeyRelatedField

class GapClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GapClassification
        fields = ['id', 'name', 'description']


class GapSerializer(serializers.ModelSerializer):
    classificationId = SafePrimaryKeyRelatedField(
        source='classification',
        queryset=GapClassification.objects.all(),
        required=False,
        allow_null=True
    )
    ownerIds = SafePrimaryKeyRelatedField(
        source='owner_ids',
        queryset=Developer.objects.all(),
        many=True,
        required=False
    )
    useCaseIds = SafePrimaryKeyRelatedField(
        source='use_cases',
        queryset=UseCase.objects.all(),
        many=True,
        required=False
    )
    dueDate = serializers.CharField(source='due_date', required=False, allow_blank=True)

    class Meta:
        model = Gap
        fields = [
            'id', 'title', 'description', 'classificationId',
            'status', 'priority', 'ownerIds', 'useCaseIds', 'dueDate',
            'dependency', 'resolution'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if ret.get('classificationId') is None:
            ret['classificationId'] = ''
        return ret
