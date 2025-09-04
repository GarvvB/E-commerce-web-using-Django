# Work of serializer : It is a predefined /methodology inside the python rest framework. In this the json data is converted into table form
# To install = pip install djangorestframework

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import SellerRegistration, UserRegistration

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerRegistration
        fields = '__all__'

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegistration
        fields = '__all__'