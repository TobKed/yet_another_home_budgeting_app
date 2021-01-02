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

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise CommandError('User with email "%s" does not exist' % user_email)

        expenditure_count_start = Expenditure.objects.filter(user=user).count()

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully found user: "%s"\n'
                "User Expenditure count: %d" % (user_email, expenditure_count_start)
            )
        )

        if not os.path.isfile(file):
            raise CommandError('File "%s" does not exist' % file)

        categories = self._read_categories_from_csv(file)
        self._categories_registry = {c: None for c in categories}
        self._populate_categories(categories, user)

        # for poll_id in options['poll_id']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()

        self.stdout.write(
            self.style.SUCCESS(
                '_categories_registry  "%s"' % str(self._categories_registry)
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully executed command. Options:  "%s"' % str(options)
            )
        )

    def _read_categories_from_csv(self, file):
        category_paths = set()
        with open(file, newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                category = row[2]

                category_paths.add(category)

        return category_paths

    def _populate_categories(self, categories, user, parent_id=None):
        for category_path in categories:
            if self._categories_registry.get(category_path) is not None:
                continue

            category_path_list = category_path.split("-")
            category_name = category_path_list[-1].capitalize()
            category_path_list_length = len(category_path_list)
            if len(category_path_list) == 1:
                category_in_db = Category.objects.get_or_create(
                    user=user, name=category_name, parent_id=parent_id
                )[0]
                self._categories_registry.update({category_path: category_in_db.id})
            else:
                for i in range(category_path_list_length):
                    parent_category_path_list = category_path_list[slice(0, i)]
                    parent_category_path = "-".join(parent_category_path_list)

                    self.stdout.write(
                        self.style.WARNING('parent:  "%s"' % str(parent_category_path))
                    )

                    children_category_last_name = category_path_list[slice(i, i + 1)][0]

                    children_category_path = (
                        "-".join([parent_category_path, children_category_last_name])
                        if parent_category_path_list
                        else children_category_last_name
                    )

                    self.stdout.write(
                        self.style.WARNING(
                            'children:  "%s"' % str(children_category_path)
                        )
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

                    self.stdout.write(self.style.WARNING('p_id:  "%s"' % str(p_id)))

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
            self.style.SUCCESS('debug:  "%s"' % str(self._categories_registry))
        )
