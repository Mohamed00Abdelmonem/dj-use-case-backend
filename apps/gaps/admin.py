from django.contrib import admin

from .models import Gap, GapClassification


admin.site.register(GapClassification)
admin.site.register(Gap)
