from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Category, Expenditure

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Expenditure)
