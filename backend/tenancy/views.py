from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Organization
from .permissions import IsOrgAdmin, IsViewerOrAbove
from .serializers import OrganizationSerializer, UserCreateSerializer, UserSerializer

User = get_user_model()


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrgAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(id=self.request.user.organization_id)


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsViewerOrAbove]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        if user.role == 'admin':
            return User.objects.filter(organization=user.organization)
        return User.objects.filter(id=user.id)

    def perform_create(self, serializer):
        user = self.request.user
        if not (user.is_superuser or user.role == 'admin'):
            raise PermissionDenied('Only admins can create users.')
        if not user.is_superuser and serializer.validated_data.get('organization') != user.organization:
            serializer.validated_data['organization'] = user.organization
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_superuser or user.role == 'admin'):
            raise PermissionDenied('Only admins can update users.')
        serializer.save()

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
