from rest_framework import serializers
from account.models import Citizen
from complaint.models import Complaint
from schemes.models import Scheme
from funds.models import Fund, Project


class CitizenSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Citizen
        fields = [
            "id", "user", "full_name", "email", "phone", "aadhaar",
            "gender", "district", "taluka", "village", "ward", "pincode", "address"
        ]
        read_only_fields = ["user"]

    def get_full_name(self, obj):
        return obj.user.get_full_name()


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"
        read_only_fields = ["complaint_id", "created_at", "updated_at"]


class ProjectSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id", "fund", "name", "sanctioned_amount", "used_amount",
            "status", "start_date", "end_date", "created_at", "updated_at",
            "progress_percentage"
        ]
        read_only_fields = ["created_at", "updated_at"]


class FundSerializer(serializers.ModelSerializer):
    used_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    projects = ProjectSerializer(many=True, read_only=True)

    class Meta:
        model = Fund
        fields = [
            "id", "title", "department", "total_amount", "released_amount",
            "location", "year", "created_at", "updated_at",
            "used_amount", "remaining_amount", "projects"
        ]
        read_only_fields = ["created_at", "updated_at"]


class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = [
            "id", "title", "slug", "description", "eligibility", "benefits",
            "category", "level", "state", "district", "taluka", "village",
            "official_link", "image", "is_verified", "created_at", "updated_at"
        ]
        read_only_fields = ["slug", "created_at", "updated_at", "is_verified"]