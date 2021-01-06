from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ExpenditureForm
from .models import Category, Expenditure


def categories_list_view(request):
    categories_with_related_count = Category.objects.add_related_count(
        Category.objects.all(), Expenditure, "category", "o_count", cumulative=True
    )

    return render(
        request, "budget/categories.html", {"categories": categories_with_related_count}
    )


class ExpenditureList(LoginRequiredMixin, ListView):
    model = Expenditure
    paginate_by = 20

    def get_queryset(self):
        return Expenditure.objects.filter(user=self.request.user).order_by("-spent_at")


class ExpenditureDetailView(DetailView):
    model = Expenditure


class ExpenditureCreateView(LoginRequiredMixin, CreateView):
    model = Expenditure
    form_class = ExpenditureForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExpenditureUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Expenditure
    fields = ["value", "spent_at", "comment", "category"]

    def get_form_class(self):
        return ExpenditureForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def test_func(self):
        obj = self.get_object()
        if self.request.user == obj.user:
            return True
        return False


class ExpenditureDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Expenditure
    success_url = reverse_lazy("budget:expenditure_list_view")

    def test_func(self):
        obj = self.get_object()
        if self.request.user == obj.user:
            return True
        return False
