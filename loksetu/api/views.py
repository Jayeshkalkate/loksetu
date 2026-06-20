from rest_framework import generics

from account.models import Citizen
from complaint.models import complaint
from schemes.models import Scheme
from funds.models import Fund, Project

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import (
    CitizenSerializer,
    ComplaintSerializer,
    SchemeSerializer,
    ProjectSerializer,
    FundSerializer
)


class CitizenAPIView(generics.ListCreateAPIView):
    queryset = Citizen.objects.all()
    serializer_class = CitizenSerializer


class ComplaintAPIView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        'status',
        'district',
        'department'
    ]

    search_fields = [
        'title',
        'description',
        'full_name'
    ]

    ordering_fields = [
        'complaint_id'
    ]


class SchemeAPIView(generics.ListCreateAPIView):
    queryset = Scheme.objects.all()
    serializer_class = SchemeSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        'category',
        'level',
        'is_verified'
    ]

    search_fields = [
        'title',
        'description',
        'benefits'
    ]

    ordering_fields = [
        'title'
    ]


class ProjectAPIView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        'status'
    ]

    search_fields = [
        'name'
    ]

    ordering_fields = [
        'created_at',
        'used_amount',
        'sanctioned_amount'
    ]


class FundAPIView(generics.ListCreateAPIView):
    queryset = Fund.objects.all()
    serializer_class = FundSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        'year',
        'department'
    ]

    search_fields = [
        'title',
        'department'
    ]

    ordering_fields = [
        'year',
        'total_amount',
        'released_amount'
    ]
    
    
