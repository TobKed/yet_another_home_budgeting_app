from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BudgetConfig(AppConfig):
    name = "yet_another_home_budgeting_app.budget"
    verbose_name = _("Budget")
