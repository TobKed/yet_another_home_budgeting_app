from django.urls import path

from .views import categories_list_view

app_name = "budget"
urlpatterns = [
    path("categories/", view=categories_list_view, name="categories_list_view"),
]
