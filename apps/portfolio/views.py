from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone

from .models import Domain, Category, UseCase, Pipeline
from .serializers import DomainSerializer, CategorySerializer, UseCaseSerializer, PipelineSerializer
from apps.people.models import Developer
from apps.people.serializers import DeveloperSerializer
from apps.gaps.models import GapClassification, Gap
from apps.gaps.serializers import GapClassificationSerializer, GapSerializer
from apps.integrations.models import Integration, NAR
from apps.integrations.serializers import IntegrationSerializer, NarSerializer

DEFAULT_USE_CASE_STATUSES = ["Not Assessed", "In Assessment", "Gaps Identified", "Ready", "Implemented"]
DEFAULT_GAP_STATUSES = ["Open", "In Analysis", "Planned", "In Progress", "Blocked", "Closed"]
DEFAULT_PRIORITIES = ["Low", "Medium", "High", "Critical"]
DEFAULT_INTEGRATION_STATUSES = ["Not Started", "Planned", "In Progress", "Available", "Blocked"]
DEFAULT_PIPELINE_STATUSES = ["Planned", "In Development", "Active", "Paused", "Failed", "Retired"]
DEFAULT_PIPELINE_ENVIRONMENTS = ["Development", "Test", "UAT", "Production"]
DEFAULT_NAR_STATUSES = ["Draft", "Submitted", "Approved", "Rejected", "Revoked"]

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

    @action(detail=True, methods=['patch', 'post'], url_path='status')
    def change_status(self, request, pk=None):
        use_case = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "Field 'status' is required."}, status=status.HTTP_400_BAD_REQUEST)
        use_case.status = new_status
        use_case.save()
        serializer = self.get_serializer(use_case)
        return Response(serializer.data)


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all().prefetch_related('integration_ids', 'use_case_ids', 'owner_ids')
    serializer_class = PipelineSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'environment', 'type']
    search_fields = ['name', 'uuid', 'server', 'description', 'notes']
    ordering_fields = ['name', 'status', 'created_at']


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
        nars = NAR.objects.all().prefetch_related('integration_ids', 'owner_ids')
        pipelines = Pipeline.objects.all().prefetch_related('integration_ids', 'use_case_ids', 'owner_ids')

        return Response({
            "meta": {
                "app": "Use Case Hub",
                "version": "2.5",
                "updatedAt": timezone.now().isoformat()
            },
            "settings": {
                "useCaseStatuses": DEFAULT_USE_CASE_STATUSES,
                "gapStatuses": DEFAULT_GAP_STATUSES,
                "priorities": DEFAULT_PRIORITIES,
                "integrationStatuses": DEFAULT_INTEGRATION_STATUSES,
                "catalogueWidth": 310,
                "pipelineStatuses": DEFAULT_PIPELINE_STATUSES,
                "pipelineEnvironments": DEFAULT_PIPELINE_ENVIRONMENTS,
                "narStatuses": DEFAULT_NAR_STATUSES,
                "narRenewalWarningDays": 30
            },
            "domains": DomainSerializer(domains, many=True).data,
            "integrations": IntegrationSerializer(integrations, many=True).data,
            "developers": DeveloperSerializer(developers, many=True).data,
            "gapClassifications": GapClassificationSerializer(gap_classifications, many=True).data,
            "gaps": GapSerializer(gaps, many=True).data,
            "nars": NarSerializer(nars, many=True).data,
            "pipelines": PipelineSerializer(pipelines, many=True).data
        })


class PortfolioImportView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        if not isinstance(data, dict):
            return Response({"error": "Invalid payload format. Expected JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        Pipeline.objects.all().delete()
        NAR.objects.all().delete()
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

        uc_map = {}
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
                    uc_map[uc.id] = uc
                    for d_id in uc_data.get('developerIds', []):
                        if d_id in dev_map:
                            uc.developer_ids.add(dev_map[d_id])
                    for i_id in uc_data.get('integrationIds', []):
                        if i_id in int_map:
                            uc.integration_ids.add(int_map[i_id])
                    for g_id in uc_data.get('gapIds', []):
                        if g_id in gap_map:
                            uc.gap_ids.add(gap_map[g_id])

        for nar_data in data.get('nars', []):
            nar = NAR.objects.create(
                id=nar_data.get('id'),
                number=nar_data.get('number', ''),
                status=nar_data.get('status', 'Draft'),
                request_date=nar_data.get('requestDate', ''),
                end_date=nar_data.get('endDate', ''),
                warning_days=nar_data.get('warningDays', 30),
                mail_subject=nar_data.get('mailSubject', ''),
                requester=nar_data.get('requester', ''),
                approval_reference=nar_data.get('approvalReference', ''),
                access_scope=nar_data.get('accessScope', ''),
                notes=nar_data.get('notes', '')
            )
            for i_id in nar_data.get('integrationIds', []):
                if i_id in int_map:
                    nar.integration_ids.add(int_map[i_id])
            for o_id in nar_data.get('ownerIds', []):
                if o_id in dev_map:
                    nar.owner_ids.add(dev_map[o_id])

        for pipe_data in data.get('pipelines', []):
            pipeline = Pipeline.objects.create(
                id=pipe_data.get('id'),
                name=pipe_data.get('name', ''),
                uuid=pipe_data.get('uuid', ''),
                type=pipe_data.get('type', 'Batch'),
                status=pipe_data.get('status', 'Planned'),
                server=pipe_data.get('server', ''),
                server_url=pipe_data.get('serverUrl', ''),
                environment=pipe_data.get('environment', 'Development'),
                schedule=pipe_data.get('schedule', ''),
                timezone=pipe_data.get('timezone', 'UTC'),
                repository_url=pipe_data.get('repositoryUrl', ''),
                pipeline_path=pipe_data.get('pipelinePath', ''),
                blocks=pipe_data.get('blocks', []),
                description=pipe_data.get('description', ''),
                notes=pipe_data.get('notes', '')
            )
            for i_id in pipe_data.get('integrationIds', []):
                if i_id in int_map:
                    pipeline.integration_ids.add(int_map[i_id])
            for uc_id in pipe_data.get('useCaseIds', []):
                if uc_id in uc_map:
                    pipeline.use_case_ids.add(uc_map[uc_id])
            for o_id in pipe_data.get('ownerIds', []):
                if o_id in dev_map:
                    pipeline.owner_ids.add(dev_map[o_id])

        return PortfolioView().get(request)
