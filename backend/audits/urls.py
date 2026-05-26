from rest_framework.routers import DefaultRouter

from .views import AnalystReviewViewSet, AuditLogViewSet

router = DefaultRouter()
router.register('audit-logs', AuditLogViewSet, basename='audit-log')
router.register('analyst-reviews', AnalystReviewViewSet, basename='analyst-review')

urlpatterns = router.urls
