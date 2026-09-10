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
    id = models.CharField(max_length=255, primary_key=True, default=generate_dom_id)
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
    id = models.CharField(max_length=255, primary_key=True, default=generate_cat_id)
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
    id = models.CharField(max_length=255, primary_key=True, default=generate_uc_id)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='use_cases')
    reference = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    business_value = models.TextField(blank=True, default='')
    outputs = models.TextField(blank=True, default='')
    status = models.CharField(max_length=255, default='Not Assessed')
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


def generate_pipe_id():
    return f"pipe-{uuid.uuid4()}"


class Pipeline(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=generate_pipe_id)
    name = models.CharField(max_length=255)
    uuid = models.CharField(max_length=255, blank=True, default='')
    type = models.CharField(max_length=255, default='Batch')
    status = models.CharField(max_length=255, default='Planned')
    server = models.CharField(max_length=255, blank=True, default='')
    server_url = models.CharField(max_length=255, blank=True, default='')
    environment = models.CharField(max_length=255, default='Development')
    schedule = models.CharField(max_length=255, blank=True, default='')
    timezone = models.CharField(max_length=255, default='UTC')
    repository_url = models.CharField(max_length=255, blank=True, default='')
    pipeline_path = models.CharField(max_length=255, blank=True, default='')
    integration_ids = models.ManyToManyField(Integration, blank=True, related_name='pipelines')
    use_case_ids = models.ManyToManyField(UseCase, blank=True, related_name='pipelines')
    owner_ids = models.ManyToManyField(Developer, blank=True, related_name='pipelines')
    blocks = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_pipe_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
