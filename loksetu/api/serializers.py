from rest_framework import serializers

from account.models import Citizen
from complaint.models import Complaint
from schemes.models import Scheme
from funds.models import Fund, Project

class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = "__all__"
        

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = "__all__"
        
        
class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = "__all__"
        
        
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        
        
class FundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fund
        fields = "__all__"
        
        
