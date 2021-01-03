import csv
import os.path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from yet_another_home_budgeting_app.budget.models import Category, Expenditure

User = get_user_model()


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._categories_registry: dict = {}

    help = "Import legacy csv"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Budget csv filename to be parsed")
        parser.add_argument("user_email", type=str, help="User email")

    def handle(self, *args, **options):
        file = options["file"]
        user_email = options["user_email"]
        user = self._get_user(user_email)

        self.print_info_about_categories_and_expenditures_count(user)
        self.check_is_file_exists(file)

        categories = self._read_categories_from_csv(file)
        self._populate_categories(categories, user)

        self.print_info_about_categories_and_expenditures_count(user)

    def _get_user(self, user_email):
        try:
            user = User.objects.get(email=user_email)
            self.stdout.write(
                self.style.SUCCESS('Successfully found user: "%s"\n' % user_email)
            )
            return user
        except User.DoesNotExist:
            raise CommandError('User with email "%s" does not exist' % user_email)

    def print_info_about_categories_and_expenditures_count(self, user):
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
    def check_is_file_exists(file):
        """Raise error if file does not exists"""
        if not os.path.isfile(file):
            raise CommandError('File "%s" does not exist' % file)

    def _read_categories_from_csv(self, file):
        category_paths = set()
        with open(file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                category = row[2]

                category_paths.add(category)

        return category_paths

    def _populate_categories(self, categories, user):
        """Populate self._categories_registry"""
        self._categories_registry = {c: None for c in categories}
        for category_path in categories:
            if self._categories_registry.get(category_path) is not None:
                continue

            category_path_list = category_path.split("-")
            for i in range(len(category_path_list)):
                parent_category_path_list = category_path_list[slice(0, i)]
                parent_category_path = "-".join(parent_category_path_list)
                children_category_last_name = category_path_list[slice(i, i + 1)][0]

                children_category_path = (
                    "-".join([parent_category_path, children_category_last_name])
                    if parent_category_path_list
                    else children_category_last_name
                )

                if parent_category_path and not self._categories_registry.get(
                    parent_category_path
                ):
                    category_in_db = Category.objects.get_or_create(
                        user=user,
                        name=parent_category_path[-1].capitalize(),
                        parent_id=self._categories_registry.get(
                            "-".join(parent_category_path[0:-1])
                        ),
                    )[0]
                    self._categories_registry.update(
                        {parent_category_path: category_in_db.id}
                    )

                p_id = self._categories_registry.get(parent_category_path)

                if not self._categories_registry.get(children_category_path):
                    category_in_db = Category.objects.get_or_create(
                        user=user,
                        name=children_category_last_name.capitalize(),
                        parent_id=p_id,
                    )[0]
                    self._categories_registry.update(
                        {children_category_path: category_in_db.id}
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Created category:  "%s"\n'
                            "\tpath: %s" % (str(category_in_db), children_category_path)
                        )
                    )
