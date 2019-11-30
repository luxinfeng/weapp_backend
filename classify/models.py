from django.db import models

# Create your models here.
class USER_PIC(models.Model):
    user = models.CharField(max_length=30)
    pic = models.CharField(max_length=30)
    result = models.CharField(max_length=30)