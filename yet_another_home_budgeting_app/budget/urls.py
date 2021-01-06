from django.urls import path

from .views import (
    ExpenditureCreateView,
    ExpenditureDeleteView,
    ExpenditureDetailView,
    ExpenditureList,
    ExpenditureUpdateView,
    categories_list_view,
)

app_name = "budget"
urlpatterns = [
    path("categories/", view=categories_list_view, name="categories_list_view"),
    path("expenditure/", ExpenditureList.as_view(), name="expenditure_list_view"),
    path(
        "expenditure/<int:pk>/",
        ExpenditureDetailView.as_view(),
        name="expenditure_detail_view",
    ),
    path(
        "expenditure/new/",
        ExpenditureCreateView.as_view(),
        name="expenditure_create_view",
    ),
    path(
        "expenditure/<int:pk>/update/",
        ExpenditureUpdateView.as_view(),
        name="expenditure_update_view",
    ),
    path(
        "expenditure/<int:pk>/delete/",
        ExpenditureDeleteView.as_view(),
        name="expenditure_delete_view",
    ),
]
