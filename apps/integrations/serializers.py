from rest_framework import serializers
from .models import Integration

class IntegrationSerializer(serializers.ModelSerializer):
    ownerId = serializers.CharField(source='owner_id', required=False, allow_blank=True)
    dataObjects = serializers.CharField(source='data_objects', required=False, allow_blank=True)

    class Meta:
        model = Integration
        fields = [
            'id', 'name', 'system', 'source', 'type', 'direction',
            'status', 'owner', 'ownerId', 'frequency', 'dataObjects', 'description'
        ]
