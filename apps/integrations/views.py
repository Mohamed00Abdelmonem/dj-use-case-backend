from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Integration, NAR
from .serializers import IntegrationSerializer, NarSerializer

class IntegrationViewSet(viewsets.ModelViewSet):
    queryset = Integration.objects.all().prefetch_related('use_cases')
    serializer_class = IntegrationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'direction', 'system']
    search_fields = ['name', 'system', 'owner', 'description', 'data_objects']
    ordering_fields = ['name', 'status', 'system']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)



class NarViewSet(viewsets.ModelViewSet):
    queryset = NAR.objects.all().prefetch_related('integration_ids', 'owner_ids')
    serializer_class = NarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['number', 'mail_subject', 'requester', 'approval_reference', 'notes']
    ordering_fields = ['number', 'status', 'created_at']
