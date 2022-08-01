from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import *

class BioSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    class Meta:
        model = Bio
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField()
    developer = serializers.CharField(allow_blank=True, allow_null=True)
    class Meta:
        model = Project
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):
    BidSentBy = serializers.CharField()
    job = serializers.CharField()
    class Meta:
        model = Bid
        fields = '__all__'

class PortfolioSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField()
    class Meta:
        model = Portfolio
        fields = '__all__'


class DecideBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ('status')

class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    class Meta:
        model = User
        fields = ('username','email','password')


