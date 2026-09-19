from rest_framework import serializers

from .models import AIAgent, AIMessage, AISession, Recommendation


class AIAgentSerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source="courses.count", read_only=True)

    class Meta:
        model = AIAgent
        fields = [
            "id",
            "code",
            "name",
            "specialty",
            "personality",
            "expertise",
            "color",
            "course_count",
        ]


class AIMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIMessage
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = fields


class AISessionSerializer(serializers.ModelSerializer):
    agent = AIAgentSerializer(read_only=True)
    messages = AIMessageSerializer(many=True, read_only=True)

    class Meta:
        model = AISession
        fields = ["id", "agent", "agent_id", "course", "lesson", "title", "status", "messages", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at", "messages"]


class ChatPromptSerializer(serializers.Serializer):
    content = serializers.CharField()
    agent_id = serializers.IntegerField(required=False)
    course_id = serializers.IntegerField(required=False)
    lesson_id = serializers.IntegerField(required=False)


class RecommendationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_slug = serializers.CharField(source="course.slug", read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id",
            "course",
            "course_title",
            "course_slug",
            "reason",
            "score",
            "rationale",
            "is_dismissed",
            "created_at",
        ]
        read_only_fields = fields