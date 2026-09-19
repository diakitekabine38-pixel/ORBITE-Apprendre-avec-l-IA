from django.contrib import admin

from .models import AIAgent, AIContext, AIMemory, AIMessage, AISession, Recommendation


@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "specialty", "is_active")
    list_filter = ("is_active",)


@admin.register(AISession)
class AISessionAdmin(admin.ModelAdmin):
    list_display = ("user", "agent", "course", "status")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "content", "created_at")
    list_filter = ("role",)


@admin.register(AIMemory)
class AIMemoryAdmin(admin.ModelAdmin):
    list_display = ("user", "agent", "category", "key")


@admin.register(AIContext)
class AIContextAdmin(admin.ModelAdmin):
    list_display = ("course", "source")


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "reason", "score")