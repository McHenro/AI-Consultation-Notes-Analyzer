from rest_framework.routers import DefaultRouter
from .views import NoteAnalysisViewSet

router = DefaultRouter()
router.register("analyses", NoteAnalysisViewSet, basename="analysis")

urlpatterns = router.urls
