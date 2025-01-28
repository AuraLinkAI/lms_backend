# stamps/serializers.py
from rest_framework import serializers
from .models import Stamp, Document


class StampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stamp
        exclude = ['user']  # Exclude user from serializer fields since it's added automatically in perform_create


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        exclude = ['user']  # Exclude user from serializer fields since it's added automatically in perform_create
