# stamps/serializers.py
from rest_framework import serializers
from .models import Stamp, Document

class StampSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stamp
        fields = '__all__'


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'file', 'timestamp', 'version']
