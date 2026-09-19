from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("categories", views.CategoryViewSet, basename="category")
router.register("courses", views.CourseViewSet, basename="course")
router.register("modules", views.ModuleViewSet, basename="module")
router.register("lessons", views.LessonViewSet, basename="lesson")
router.register("videos", views.VideoViewSet, basename="video")
router.register("reviews", views.ReviewViewSet, basename="review")

urlpatterns = router.urls