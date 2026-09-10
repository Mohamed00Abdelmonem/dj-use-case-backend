from rest_framework.views import APIView
from rest_framework.response import Response

DEFAULT_USE_CASE_STATUSES = ["Not Assessed", "In Assessment", "Gaps Identified", "Ready", "Implemented"]
DEFAULT_GAP_STATUSES = ["Open", "In Analysis", "Planned", "In Progress", "Blocked", "Closed"]
DEFAULT_PRIORITIES = ["Low", "Medium", "High", "Critical"]
DEFAULT_INTEGRATION_STATUSES = ["Not Started", "Planned", "In Progress", "Available", "Blocked"]

class SettingsView(APIView):
    def get(self, request):
        return Response({
            "useCaseStatuses": DEFAULT_USE_CASE_STATUSES,
            "gapStatuses": DEFAULT_GAP_STATUSES,
            "priorities": DEFAULT_PRIORITIES,
            "integrationStatuses": DEFAULT_INTEGRATION_STATUSES,
            "catalogueWidth": 310
        })
