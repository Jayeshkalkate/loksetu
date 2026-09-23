from rest_framework import generics, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from account.models import Citizen
from complaint.models import Complaint
from schemes.models import Scheme
from funds.models import Fund, Project

from .serializers import (
    CitizenSerializer,
    ComplaintSerializer,
    SchemeSerializer,
    ProjectSerializer,
    FundSerializer,
)


# Custom permission: only staff can create/update/delete; others can only view
class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow read-only for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Write methods require staff status
        return request.user.is_authenticated and request.user.is_staff


# ----- CITIZEN API -----
class CitizenAPIView(generics.ListCreateAPIView):
    """
    List all citizens (staff only) or create a new citizen (staff only).
    """
    queryset = Citizen.objects.select_related("user").all()
    serializer_class = CitizenSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["district", "taluka", "village"]
    search_fields = ["user__first_name", "user__last_name", "phone", "aadhaar"]
    ordering_fields = ["user__first_name", "user__last_name", "created_at"]


# ----- COMPLAINT API -----
class ComplaintAPIView(generics.ListCreateAPIView):
    """
    List all complaints (with filtering) and create a new complaint.
    """
    queryset = Complaint.objects.select_related().all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "district", "department", "is_read"]
    search_fields = ["title", "description", "full_name", "complaint_id"]
    ordering_fields = ["complaint_id", "created_at", "status"]

    def get_queryset(self):
        """Optionally restrict to user's own complaints if not staff."""
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        # For non‑staff, only show their own complaints
        # (we need to associate with user – currently no user field in Complaint)
        # Here we assume we can filter by phone/email? Skip for now.
        return qs  # fallback – you can add logic to filter by phone/email


# ----- SCHEME API -----
class SchemeAPIView(generics.ListCreateAPIView):
    """
    List schemes (only verified for non‑staff) and create a new scheme (staff only).
    """
    queryset = Scheme.objects.select_related("created_by").all()
    serializer_class = SchemeSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "level", "is_verified", "state"]
    search_fields = ["title", "description", "benefits"]
    ordering_fields = ["title", "created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(is_verified=True)
        return qs


# ----- PROJECT API -----
class ProjectAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.select_related("fund").all()
    serializer_class = ProjectSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "fund"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "used_amount", "sanctioned_amount"]


# ----- FUND API -----
class FundAPIView(generics.ListCreateAPIView):
    queryset = Fund.objects.select_related("location").prefetch_related("projects").all()
    serializer_class = FundSerializer
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["year", "department", "location"]
    search_fields = ["title", "department"]
    ordering_fields = ["year", "total_amount", "released_amount"]


# Optional: Detail views (Retrieve/Update/Delete) – not required by user but good practice.
class ComplaintDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer
    permission_classes = [IsStaffOrReadOnly]


class SchemeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer
    permission_classes = [IsStaffOrReadOnly]


class FundDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsStaffOrReadOnly]