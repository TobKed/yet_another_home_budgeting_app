import csv
from typing import List

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from yet_another_home_budgeting_app.budget.management.commands._private import (
    date_to_string,
)
from yet_another_home_budgeting_app.budget.models import Category, Expenditure

User = get_user_model()


def get_category_path(category: Category) -> str:
    return "-".join([c.name.lower() for c in category.get_ancestors(include_self=True)])


class Command(BaseCommand):
    help = "Export to legacy csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Budget csv filename")
        parser.add_argument("user_email", type=str, help="User email")

    def handle(self, *args, **options):
        file = options["file"]
        user_email = options["user_email"]
        user = self._get_user(user_email)

        self.print_info_about_categories_and_expenditures_count(user)

        expenditures = self.get_expenditures(user)
        self.save_expenditures_to_csv(expenditures, file)

        self.print_info_about_categories_and_expenditures_count(user)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully imported %d expenditures s"' % len(expenditures)
            )
        )

    def _get_user(self, user_email: str) -> User:
        try:
            user = User.objects.get(email=user_email)
            self.stdout.write(
                self.style.SUCCESS('Successfully found user: "%s"' % user_email)
            )
            return user
        except User.DoesNotExist:
            raise CommandError('User with email "%s" does not exist' % user_email)

    def print_info_about_categories_and_expenditures_count(self, user: User) -> None:
        expenditure_count_start = Expenditure.objects.filter(user=user).count()
        category_count_start = Category.objects.filter(user=user).count()
        self.stdout.write(
            self.style.SUCCESS(
                "User Categories count: %d\n"
                "User Expenditure count: %d"
                % (category_count_start, expenditure_count_start)
            )
        )

    @staticmethod
    def get_expenditures(user: User) -> List[Expenditure]:
        return Expenditure.objects.filter(user=user).order_by("spent_at")

    def save_expenditures_to_csv(
        self, expenditures: List[Expenditure], file: str
    ) -> None:
        with open(file, mode="w") as f:
            writer = csv.writer(f, delimiter=",")
            for i, e in enumerate(expenditures):
                category_path = get_category_path(e.category)
                writer.writerow(
                    [date_to_string(e.spent_at), e.value, category_path, e.comment]
                )

        self.stdout.write(self.style.SUCCESS('Saved file: "%s"' % file))
