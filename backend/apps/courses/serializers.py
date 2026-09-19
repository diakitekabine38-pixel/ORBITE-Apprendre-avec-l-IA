from rest_framework import serializers

from apps.ai.models import AIAgent

from .models import Category, Course, Lesson, Module, Resource, Review, Video


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source="courses.count", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "icon", "course_count"]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["id", "title", "duration_seconds", "provider", "hls_url", "is_free_preview"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "title", "resource_type", "url"]


class LessonBriefSerializer(serializers.ModelSerializer):
    video_duration = serializers.IntegerField(source="video_meta.duration_seconds", read_only=True, default=0)

    class Meta:
        model = Lesson
        fields = ["id", "title", "summary", "order", "is_free_preview", "estimated_minutes", "video_duration"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonBriefSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "description", "order", "lessons"]


class LessonDetailSerializer(serializers.ModelSerializer):
    video = VideoSerializer(source="video_meta", read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "summary",
            "content",
            "order",
            "is_free_preview",
            "estimated_minutes",
            "video",
            "resources",
        ]


class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    ai_mentor_name = serializers.CharField(source="ai_mentor.name", read_only=True, default=None)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "thumbnail",
            "level",
            "price",
            "is_free",
            "duration_hours",
            "category",
            "rating",
            "review_count",
            "student_count",
            "instructor_name",
            "ai_mentor_name",
        ]


class CourseDetailSerializer(CourseListSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    prerequisites = serializers.ListField(read_only=True)
    objectives = serializers.ListField(read_only=True)

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + [
            "description",
            "objectives",
            "prerequisites",
            "modules",
            "ai_mentor",
            "ai_mentor_name",
        ]


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "slug",
            "title",
            "short_description",
            "description",
            "objectives",
            "prerequisites",
            "category",
            "level",
            "price",
            "duration_hours",
            "thumbnail",
            "promo_video_key",
            "ai_mentor",
            "is_free",
            "certification_enabled",
            "min_completion_rate",
            "min_quiz_score",
        ]

    def create(self, validated):
        validated["instructor"] = self.context["request"].user
        return super().create(validated)


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "course", "rating", "comment", "status", "user_name", "created_at"]
        read_only_fields = ["id", "status", "user_name", "created_at"]

    def create(self, validated):
        validated["user"] = self.context["request"].user
        return super().create(validated)