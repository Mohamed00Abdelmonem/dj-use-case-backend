import uuid
from django.db import models
from apps.people.models import Developer

def generate_gclass_id():
    return f"gclass-{uuid.uuid4()}"

def generate_gap_id():
    return f"gap-{uuid.uuid4()}"

class GapClassification(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_gclass_id)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_gclass_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Gap(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_gap_id)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    classification = models.ForeignKey(
        GapClassification, on_delete=models.SET_NULL, null=True, blank=True, related_name='gaps'
    )
    status = models.CharField(max_length=64, default='Open')
    priority = models.CharField(max_length=64, default='Medium')
    owner_ids = models.ManyToManyField(Developer, blank=True, related_name='gaps')
    due_date = models.CharField(max_length=64, blank=True, default='')
    dependency = models.TextField(blank=True, default='')
    resolution = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_gap_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
