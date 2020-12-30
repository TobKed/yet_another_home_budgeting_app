from django.shortcuts import render

from .models import Category, Expenditure


def categories_list_view(request):
    categories_with_related_count = Category.objects.add_related_count(
        Category.objects.all(), Expenditure, "category", "o_count", cumulative=True
    )

    return render(
        request, "budget/categories.html", {"categories": categories_with_related_count}
    )
