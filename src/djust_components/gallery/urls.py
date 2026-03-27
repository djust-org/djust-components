"""URL patterns for the component gallery.

Include in your project's urls.py::

    path("gallery/", include("djust_components.gallery.urls")),
"""

from django.urls import path

from .live_views import CategoryGalleryView, GalleryIndexView
from .views import gallery_category_view, gallery_index_view, gallery_view

urlpatterns = [
    path("", GalleryIndexView.as_view(), name="gallery-index"),
    path("all/", gallery_view, name="gallery-all"),
    path("static-index/", gallery_index_view, name="gallery-static-index"),
    path("lv/<slug:category_slug>/", CategoryGalleryView.as_view(), name="gallery-category-lv"),
    path("<slug:category_slug>/", gallery_category_view, name="gallery-category"),
]
