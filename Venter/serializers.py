"""
    Serializers for Venter RESTful API Application
"""

from rest_framework import serializers
from Venter.models import File


class FileSerializer(serializers.ModelSerializer):
    ckpt_date = serializers.DateTimeField(format="%d %B %Y")
    
    class Meta:
        model = File
        fields = (
            'organisation_name', 'ckpt_date', 'id'
        )