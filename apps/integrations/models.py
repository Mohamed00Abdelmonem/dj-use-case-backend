import uuid
from django.db import models

def generate_int_id():
    return f"int-{uuid.uuid4()}"

class Integration(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_int_id)
    name = models.CharField(max_length=255)
    system = models.CharField(max_length=255, blank=True, default='')
    source = models.CharField(max_length=255, blank=True, default='')
    type = models.CharField(max_length=255, blank=True, default='')
    direction = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=64, default='Not Started')
    owner = models.CharField(max_length=255, blank=True, default='')
    owner_id = models.CharField(max_length=64, blank=True, default='')
    frequency = models.CharField(max_length=255, blank=True, default='')
    data_objects = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_int_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
