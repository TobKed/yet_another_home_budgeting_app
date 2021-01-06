from datetime import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from mptt.models import MPTTModel, TreeForeignKey

User = settings.AUTH_USER_MODEL


class Category(MPTTModel):
    """A category of the expenditure."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class MPTTMeta:
        order_insertion_by = ["name"]

    @cached_property
    def readable_path(self):
        return " - ".join(c.name for c in self.get_ancestors(include_self=True))

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, user={self.user})"

    def __str__(self):
        return self.readable_path


class Expenditure(models.Model):
    """A expenditure of the user."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    spent_at = models.DateTimeField(default=datetime.now)
    comment = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expenditures"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"user{self.user}, "
            f"value={self.value}, "
            f"spent_at={self.spent_at},"
            f"comment='{self.comment}', "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, )"
        )

    def __str__(self):
        return self.__repr__()

    def get_absolute_url(self):
        return reverse("budget:expenditure_detail_view", kwargs={"pk": self.pk})
