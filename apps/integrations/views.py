from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Integration
from .serializers import IntegrationSerializer

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'direction', 'system']
    search_fields = ['name', 'system', 'owner', 'description', 'data_objects']
    ordering_fields = ['name', 'status', 'system']
