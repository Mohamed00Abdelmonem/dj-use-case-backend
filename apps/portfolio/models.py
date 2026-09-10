import uuid
from django.db import models
from apps.people.models import Developer
from apps.gaps.models import Gap
from apps.integrations.models import Integration

def generate_dom_id():
    return f"dom-{uuid.uuid4()}"

def generate_cat_id():
    return f"cat-{uuid.uuid4()}"

def generate_uc_id():
    return f"uc-{uuid.uuid4()}"

class Domain(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_dom_id)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_dom_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_cat_id)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_cat_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.domain.name} -> {self.name}"


class UseCase(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_uc_id)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='use_cases')
    reference = models.CharField(max_length=64, blank=True, default='')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    business_value = models.TextField(blank=True, default='')
    outputs = models.TextField(blank=True, default='')
    status = models.CharField(max_length=64, default='Not Assessed')
    notes = models.TextField(blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    developer_ids = models.ManyToManyField(Developer, blank=True, related_name='use_cases')
    integration_ids = models.ManyToManyField(Integration, blank=True, related_name='use_cases')
    gap_ids = models.ManyToManyField(Gap, blank=True, related_name='use_cases')

    class Meta:
        ordering = ['reference', 'name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_uc_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference} - {self.name}"
