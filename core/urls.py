from django.urls import path, include
from .views import UploadNoteView, IndexView, NoteAnalysisViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("analyses", NoteAnalysisViewSet, basename="analysis")

# urlpatterns = router.urls

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("api/upload/", UploadNoteView.as_view(), name="upload-note"),
    path("api/", include(router.urls)),
]
