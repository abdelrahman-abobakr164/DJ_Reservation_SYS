from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Reservation, ELDay

User = get_user_model()


class AgentListSerializer(serializers.ModelSerializer):
    specialties = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "specialties"]


class WorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = ELDay
        fields = ["day_of_week", "start_time", "end_time"]


class AgentDetailSerializer(serializers.ModelSerializer):
    specialties = serializers.StringRelatedField(many=True)
    working_hours = WorkingHourSerializer(many=True, read_only=True)
    graduation = serializers.StringRelatedField(many=True)
    certifications = serializers.StringRelatedField(many=True)
    recent_achievements = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "specialties",
            "working_hours",
            "graduation",
            "certifications",
            "recent_achievements",
        ]


class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["full_name", "email", "subject", "date", "time"]


class ReservationSerializer(serializers.ModelSerializer):
    agent = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "agent",
            "full_name",
            "email",
            "subject",
            "date",
            "time",
            "status",
        ]
        read_only_fields = fields
