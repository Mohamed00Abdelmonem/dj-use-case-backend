from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import GapClassification, Gap
from .serializers import GapClassificationSerializer, GapSerializer

class GapClassificationViewSet(viewsets.ModelViewSet):
    queryset = GapClassification.objects.all()
    serializer_class = GapClassificationSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


class GapViewSet(viewsets.ModelViewSet):
    queryset = Gap.objects.all().prefetch_related('owner_ids', 'use_cases')
    serializer_class = GapSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'classification']
    search_fields = ['title', 'description', 'dependency', 'resolution']
    ordering_fields = ['title', 'status', 'priority']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

