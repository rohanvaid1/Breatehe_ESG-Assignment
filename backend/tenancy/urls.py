from rest_framework.routers import DefaultRouter

from .views import OrganizationViewSet, UserViewSet

router = DefaultRouter()
router.register('organizations', OrganizationViewSet, basename='organization')
router.register('users', UserViewSet, basename='user')

urlpatterns = router.urls
