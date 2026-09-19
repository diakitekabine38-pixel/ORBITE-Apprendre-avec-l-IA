from django.contrib import admin

from .models import Enrollment, Goal, LearningPath, LessonProgress, Skill, UserSkill


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "progress", "completed")
    list_filter = ("completed",)


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ("enrollment", "lesson", "status", "progress_percent")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "category")


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ("user", "skill", "mastery_score", "confidence")


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "status")


@admin.register(LearningPath)
class LearningPathAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_active")