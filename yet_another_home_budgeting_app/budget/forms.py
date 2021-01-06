from datetime import datetime

from django import forms
from mptt.forms import TreeNodeChoiceField

from yet_another_home_budgeting_app.budget.models import Category, Expenditure


class ExpenditureForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all())
    spent_at = forms.DateTimeField(
        initial=datetime.now,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Expenditure
        fields = ("value", "spent_at", "comment", "category")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(user=user)
