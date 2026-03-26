"""URL patterns for the component gallery.

Include in your project's urls.py::

    path("gallery/", include("djust_components.gallery.urls")),
"""

from django.urls import path

from .views import gallery_category_view, gallery_index_view, gallery_view

urlpatterns = [
    path("", gallery_index_view, name="gallery-index"),
    path("all/", gallery_view, name="gallery-all"),
    path("<slug:category_slug>/", gallery_category_view, name="gallery-category"),
]
