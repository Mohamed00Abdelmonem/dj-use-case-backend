from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from apps.portfolio.models import Domain, UseCase
from apps.gaps.models import Gap
from apps.integrations.models import Integration
from apps.core.views import DEFAULT_GAP_STATUSES, DEFAULT_PRIORITIES, DEFAULT_INTEGRATION_STATUSES

class AnalyticsView(APIView):
    def get(self, request):
        domains = Domain.objects.annotate(
            use_case_count=Count('categories__use_cases')
        )
        domain_rows = [[d.name, d.use_case_count] for d in domains]

        open_gaps_qs = Gap.objects.exclude(status='Closed')
        open_gap_rows = []
        for p in DEFAULT_PRIORITIES:
            cnt = open_gaps_qs.filter(priority=p).count()
            open_gap_rows.append([p, cnt])

        gap_status_rows = []
        for s in DEFAULT_GAP_STATUSES:
            cnt = Gap.objects.filter(status=s).count()
            gap_status_rows.append([s, cnt])

        integration_rows = []
        for s in DEFAULT_INTEGRATION_STATUSES:
            cnt = Integration.objects.filter(status=s).count()
            integration_rows.append([s, cnt])

        total_use_cases = UseCase.objects.count()
        total_gaps = Gap.objects.count()
        open_gaps_count = open_gaps_qs.count()
        critical_count = open_gaps_qs.filter(priority='Critical').count()
        ready_integrations_count = Integration.objects.filter(status='Available').count()

        return Response({
            "kpis": {
                "totalUseCases": total_use_cases,
                "totalGaps": total_gaps,
                "openGaps": open_gaps_count,
                "criticalGaps": critical_count,
                "readyIntegrations": ready_integrations_count
            },
            "charts": {
                "useCasesByDomain": domain_rows,
                "openGapsByPriority": open_gap_rows,
                "gapStatus": gap_status_rows,
                "integrationReadiness": integration_rows
            }
        })
