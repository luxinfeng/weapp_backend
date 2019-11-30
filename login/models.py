
from django.db import models
from django.utils import timezone
class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    user_times = models.IntegerField()