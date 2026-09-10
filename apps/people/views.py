from rest_framework import viewsets, filters
from .models import Developer
from .serializers import DeveloperSerializer

class DeveloperViewSet(viewsets.ModelViewSet):
    queryset = Developer.objects.all()
    serializer_class = DeveloperSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'role', 'email']
    ordering_fields = ['name', 'role']
