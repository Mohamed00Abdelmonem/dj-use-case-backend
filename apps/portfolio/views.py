from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone

from .models import Domain, Category, UseCase
from .serializers import DomainSerializer, CategorySerializer, UseCaseSerializer
from apps.people.models import Developer
from apps.people.serializers import DeveloperSerializer
from apps.gaps.models import GapClassification, Gap
from apps.gaps.serializers import GapClassificationSerializer, GapSerializer
from apps.integrations.models import Integration
from apps.integrations.serializers import IntegrationSerializer

DEFAULT_USE_CASE_STATUSES = ["Not Assessed", "In Assessment", "Gaps Identified", "Ready", "Implemented"]
DEFAULT_GAP_STATUSES = ["Open", "In Analysis", "Planned", "In Progress", "Blocked", "Closed"]
DEFAULT_PRIORITIES = ["Low", "Medium", "High", "Critical"]
DEFAULT_INTEGRATION_STATUSES = ["Not Started", "Planned", "In Progress", "Available", "Blocked"]

class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all().prefetch_related('categories__use_cases')
    serializer_class = DomainSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.categories.exists():
            return Response(
                {"error": "Cannot delete domain containing categories."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related('use_cases')
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['domain']
    search_fields = ['name', 'description']
    ordering_fields = ['order', 'name']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.use_cases.exists():
            return Response(
                {"error": "Cannot delete category containing use cases."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class UseCaseViewSet(viewsets.ModelViewSet):
    queryset = UseCase.objects.all().select_related('category', 'category__domain').prefetch_related(
        'developer_ids', 'integration_ids', 'gap_ids'
    )
    serializer_class = UseCaseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category', 'category__domain']
    search_fields = ['reference', 'name', 'description', 'notes', 'business_value', 'outputs']
    ordering_fields = ['reference', 'name', 'status', 'updated_at']


class PortfolioView(APIView):
    def get(self, request):
        domains = Domain.objects.all().prefetch_related(
            'categories__use_cases__developer_ids',
            'categories__use_cases__integration_ids',
            'categories__use_cases__gap_ids'
        )
        integrations = Integration.objects.all()
        developers = Developer.objects.all()
        gap_classifications = GapClassification.objects.all()
        gaps = Gap.objects.all().prefetch_related('owner_ids')

        return Response({
            "meta": {
                "app": "Use Case Hub",
                "version": "2.3",
                "updatedAt": timezone.now().isoformat()
            },
            "settings": {
                "useCaseStatuses": DEFAULT_USE_CASE_STATUSES,
                "gapStatuses": DEFAULT_GAP_STATUSES,
                "priorities": DEFAULT_PRIORITIES,
                "integrationStatuses": DEFAULT_INTEGRATION_STATUSES,
                "catalogueWidth": 310
            },
            "domains": DomainSerializer(domains, many=True).data,
            "integrations": IntegrationSerializer(integrations, many=True).data,
            "developers": DeveloperSerializer(developers, many=True).data,
            "gapClassifications": GapClassificationSerializer(gap_classifications, many=True).data,
            "gaps": GapSerializer(gaps, many=True).data
        })


class PortfolioImportView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return Response({"error": "Invalid payload format. Expected JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        UseCase.objects.all().delete()
        Category.objects.all().delete()
        Domain.objects.all().delete()
        Gap.objects.all().delete()
        GapClassification.objects.all().delete()
        Integration.objects.all().delete()
        Developer.objects.all().delete()

        dev_map = {}
        for dev_data in data.get('developers', []):
            dev = Developer.objects.create(
                id=dev_data.get('id'),
                name=dev_data.get('name', ''),
                role=dev_data.get('role', ''),
                email=dev_data.get('email', '')
            )
            dev_map[dev.id] = dev

        int_map = {}
        for int_data in data.get('integrations', []):
            integration = Integration.objects.create(
                id=int_data.get('id'),
                name=int_data.get('name', ''),
                system=int_data.get('system', ''),
                source=int_data.get('source', ''),
                type=int_data.get('type', ''),
                direction=int_data.get('direction', ''),
                status=int_data.get('status', 'Not Started'),
                owner=int_data.get('owner', ''),
                owner_id=int_data.get('ownerId', ''),
                frequency=int_data.get('frequency', ''),
                data_objects=int_data.get('dataObjects', ''),
                description=int_data.get('description', '')
            )
            int_map[integration.id] = integration

        class_map = {}
        for class_data in data.get('gapClassifications', []):
            gc = GapClassification.objects.create(
                id=class_data.get('id'),
                name=class_data.get('name', ''),
                description=class_data.get('description', '')
            )
            class_map[gc.id] = gc

        gap_map = {}
        for gap_data in data.get('gaps', []):
            class_id = gap_data.get('classificationId')
            gc = class_map.get(class_id) if class_id else None
            gap = Gap.objects.create(
                id=gap_data.get('id'),
                title=gap_data.get('title', ''),
                description=gap_data.get('description', ''),
                classification=gc,
                status=gap_data.get('status', 'Open'),
                priority=gap_data.get('priority', 'Medium'),
                due_date=gap_data.get('dueDate', ''),
                dependency=gap_data.get('dependency', ''),
                resolution=gap_data.get('resolution', '')
            )
            owner_ids = gap_data.get('ownerIds', [])
            for o_id in owner_ids:
                if o_id in dev_map:
                    gap.owner_ids.add(dev_map[o_id])
            gap_map[gap.id] = gap

        for dom_data in data.get('domains', []):
            domain = Domain.objects.create(
                id=dom_data.get('id'),
                name=dom_data.get('name', ''),
                description=dom_data.get('description', ''),
                order=dom_data.get('order', 1)
            )
            for cat_data in dom_data.get('categories', []):
                category = Category.objects.create(
                    id=cat_data.get('id'),
                    domain=domain,
                    name=cat_data.get('name', ''),
                    description=cat_data.get('description', ''),
                    order=cat_data.get('order', 1)
                )
                for uc_data in cat_data.get('useCases', []):
                    uc = UseCase.objects.create(
                        id=uc_data.get('id'),
                        category=category,
                        reference=uc_data.get('reference', ''),
                        name=uc_data.get('name', ''),
                        description=uc_data.get('description', ''),
                        business_value=uc_data.get('businessValue', ''),
                        outputs=uc_data.get('outputs', ''),
                        status=uc_data.get('status', 'Not Assessed'),
                        notes=uc_data.get('notes', '')
                    )
                    for d_id in uc_data.get('developerIds', []):
                        if d_id in dev_map:
                            uc.developer_ids.add(dev_map[d_id])
                    for i_id in uc_data.get('integrationIds', []):
                        if i_id in int_map:
                            uc.integration_ids.add(int_map[i_id])
                    for g_id in uc_data.get('gapIds', []):
                        if g_id in gap_map:
                            uc.gap_ids.add(gap_map[g_id])

        return PortfolioView().get(request)
