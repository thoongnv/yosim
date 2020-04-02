from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    name = 'yosim.categories'
    verbose_name = "Categories"

    def ready(self):
        pass


