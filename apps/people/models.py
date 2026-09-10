import uuid
from django.db import models

def generate_dev_id():
    return f"dev-{uuid.uuid4()}"

class Developer(models.Model):
    id = models.CharField(max_length=64, primary_key=True, default=generate_dev_id)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, default='')
    email = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_dev_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
