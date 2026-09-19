from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("quizzes", views.QuizViewSet, basename="quiz")
router.register("attempts", views.AttemptViewSet, basename="attempt")
router.register("exercises", views.ExerciseViewSet, basename="exercise")
router.register("submissions", views.SubmissionViewSet, basename="submission")

urlpatterns = router.urls