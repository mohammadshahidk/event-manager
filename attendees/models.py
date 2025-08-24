from django.db import models


class Attendees(models.Model):
    """
    """
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.name} {self.email}"
    
