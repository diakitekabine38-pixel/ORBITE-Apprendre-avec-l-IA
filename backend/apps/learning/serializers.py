from rest_framework import serializers

from apps.courses.serializers import CourseListSerializer
from apps.courses.models import Course

from .models import (
    Enrollment,
    Goal,
    LearningPath,
    LessonProgress,
    Skill,
    UserSkill,
)


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source="course", queryset=Course.objects.all(), write_only=True
    )

    class Meta:
        model = Enrollment
        fields = ["id", "course", "course_id", "progress", "completed", "completed_at", "created_at"]
        read_only_fields = ["id", "progress", "completed", "completed_at", "created_at"]

    def create(self, validated):
        user = self.context["request"].user
        course = validated.pop("course")
        enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
        return enrollment


class LessonProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_order = serializers.IntegerField(source="lesson.order", read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "lesson_order",
            "status",
            "progress_percent",
            "seconds_watched",
            "last_position",
            "completed_at",
        ]
        read_only_fields = ["id", "completed_at"]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "slug", "category", "description"]


class UserSkillSerializer(serializers.ModelSerializer):
    skill_detail = SkillSerializer(source="skill", read_only=True)

    class Meta:
        model = UserSkill
        fields = ["id", "skill", "skill_detail", "mastery_score", "confidence", "last_assessed_at"]
        read_only_fields = ["id", "last_assessed_at"]


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "title", "description", "target_date", "status", "courses", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated):
        validated["user"] = self.context["request"].user
        return super().create(validated)


class LearningPathSerializer(serializers.ModelSerializer):
    courses = CourseListSerializer(many=True, read_only=True)

    class Meta:
        model = LearningPath
        fields = ["id", "title", "description", "courses", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated):
        validated["user"] = self.context["request"].user
        return super().create(validated)