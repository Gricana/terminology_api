from rest_framework import serializers

from .models import Handbook, HandbookElement


class HandbookSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Handbook.
    """

    class Meta:
        model = Handbook
        fields = ['id', 'code', 'name']


class HandbookElementSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели HandbookElement.
    """

    class Meta:
        model = HandbookElement
        fields = ['code', 'value']
