from django.contrib import admin

from .models import Category, Course, Lesson, Module, Resource, Review, Video


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "level", "price", "status", "instructor")
    list_filter = ("status", "level", "category")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_seconds", "provider")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "resource_type")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "status")