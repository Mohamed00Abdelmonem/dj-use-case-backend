import uuid
from django.db import models

def generate_int_id():
    return f"int-{uuid.uuid4()}"

class Integration(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=generate_int_id)
    name = models.CharField(max_length=255)
    system = models.CharField(max_length=255, blank=True, default='')
    source = models.CharField(max_length=255, blank=True, default='')
    type = models.CharField(max_length=255, blank=True, default='')
    direction = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=255, default='Not Started')
    owner = models.CharField(max_length=255, blank=True, default='')
    owner_id = models.CharField(max_length=255, blank=True, default='')
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


def generate_nar_id():
    return f"nar-{uuid.uuid4()}"


class NAR(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=generate_nar_id)
    number = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default='Draft')
    request_date = models.CharField(max_length=255, blank=True, default='')
    end_date = models.CharField(max_length=255, blank=True, default='')
    warning_days = models.IntegerField(default=30)
    mail_subject = models.CharField(max_length=255, blank=True, default='')
    requester = models.CharField(max_length=255, blank=True, default='')
    approval_reference = models.CharField(max_length=255, blank=True, default='')
    integration_ids = models.ManyToManyField(Integration, blank=True, related_name='nars')
    owner_ids = models.ManyToManyField('people.Developer', blank=True, related_name='nars')
    access_scope = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_nar_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.number
