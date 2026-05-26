from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AirportLookupViewSet,
    AnomalyFlagViewSet,
    DashboardMetricsView,
    EmissionCategoryViewSet,
    NormalizedRecordViewSet,
    PlantLookupViewSet,
    SourceSystemViewSet,
    UnitConversionViewSet,
    UploadBatchViewSet,
)

router = DefaultRouter()
router.register('source-systems', SourceSystemViewSet, basename='source-system')
router.register('upload-batches', UploadBatchViewSet, basename='upload-batch')
router.register('normalized-records', NormalizedRecordViewSet, basename='normalized-record')
router.register('anomalies', AnomalyFlagViewSet, basename='anomaly')
router.register('emission-categories', EmissionCategoryViewSet, basename='emission-category')
router.register('unit-conversions', UnitConversionViewSet, basename='unit-conversion')
router.register('plants', PlantLookupViewSet, basename='plant-lookup')
router.register('airports', AirportLookupViewSet, basename='airport-lookup')

urlpatterns = [
    path('dashboard/metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
]

urlpatterns += router.urls
