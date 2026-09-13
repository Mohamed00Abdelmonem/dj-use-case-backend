from django.contrib import admin

from .models import Category, Domain, Pipeline, UseCase


admin.site.register(Domain)
admin.site.register(Category)
admin.site.register(UseCase)
admin.site.register(Pipeline)
