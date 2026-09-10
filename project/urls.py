from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.core.views import SettingsView
from apps.people.views import DeveloperViewSet
from apps.gaps.views import GapClassificationViewSet, GapViewSet
from apps.integrations.views import IntegrationViewSet
from apps.portfolio.views import (
    DomainViewSet, CategoryViewSet, UseCaseViewSet,
    PortfolioView, PortfolioImportView
)
from apps.analytics.views import AnalyticsView

router = DefaultRouter()
router.register(r'domains', DomainViewSet, basename='domain')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'use-cases', UseCaseViewSet, basename='usecase')
router.register(r'developers', DeveloperViewSet, basename='developer')
router.register(r'gap-classifications', GapClassificationViewSet, basename='gapclassification')
router.register(r'gaps', GapViewSet, basename='gap')
router.register(r'integrations', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/portfolio/', PortfolioView.as_view(), name='portfolio-detail'),
    path('api/portfolio/import/', PortfolioImportView.as_view(), name='portfolio-import'),
    path('api/settings/', SettingsView.as_view(), name='settings-detail'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics-detail'),
    path('api/', include(router.urls)),
]
