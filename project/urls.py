from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter


from apps.core.views import SettingsView
from apps.people.views import DeveloperViewSet
from apps.gaps.views import GapClassificationViewSet, GapViewSet
from apps.integrations.views import IntegrationViewSet, NarViewSet
from apps.portfolio.views import (
    DomainViewSet, CategoryViewSet, UseCaseViewSet, PipelineViewSet,
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
router.register(r'nars', NarViewSet, basename='nar')
router.register(r'pipelines', PipelineViewSet, basename='pipeline')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/portfolio/', PortfolioView.as_view(), name='portfolio-detail'),
    path('api/portfolio/import/', PortfolioImportView.as_view(), name='portfolio-import'),
    path('api/settings/', SettingsView.as_view(), name='settings-detail'),
    path('api/analytics/', AnalyticsView.as_view(), name='analytics-detail'),
    path('api/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

