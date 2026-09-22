from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register("progress", views.LessonProgressViewSet, basename="lesson-progress")
router.register("skills", views.SkillViewSet, basename="skill")
router.register("user-skills", views.UserSkillViewSet, basename="user-skill")
router.register("goals", views.GoalViewSet, basename="goal")
router.register("paths", views.LearningPathViewSet, basename="learning-path")

urlpatterns = router.urls + [path("orbite/", views.orbite, name="orbite")]