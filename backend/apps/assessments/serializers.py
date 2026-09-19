from rest_framework import serializers

from apps.courses.models import Lesson

from .models import Attempt, Exercise, Question, Quiz, Submission

XP_QUIZ = 50
XP_EXERCISE = 80


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # `correct` never returned to the client; grading happens server-side.
        fields = ["id", "question_type", "text", "options", "points"]
        read_only_fields = fields


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "lesson",
            "title",
            "quiz_type",
            "pass_score",
            "max_attempts",
            "instructions",
            "time_limit_minutes",
            "questions",
        ]
        read_only_fields = ["id", "questions"]


class AttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)

    class Meta:
        model = Attempt
        fields = [
            "id",
            "quiz",
            "quiz_title",
            "score",
            "passed",
            "time_spent_seconds",
            "completed_at",
        ]
        read_only_fields = fields


class AttemptCreateSerializer(serializers.Serializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    answers = serializers.JSONField()
    time_spent_seconds = serializers.IntegerField(default=0, min_value=0)


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "lesson", "title", "instructions", "exercise_type"]
        read_only_fields = ["id"]


class SubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source="exercise.title", read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "exercise",
            "exercise_title",
            "user_name",
            "content",
            "status",
            "ai_score",
            "human_validated",
            "feedback",
            "created_at",
        ]
        read_only_fields = ["id", "status", "ai_score", "human_validated", "feedback", "user_name", "created_at"]