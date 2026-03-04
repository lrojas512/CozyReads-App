from django.db import models

# Create your models here.
class Book (models.Model):
    STATUS_CHOICES = [
        ('want', 'Want to Read'),
        ('completed', 'Completed'),
    ]

    open_library_id = models.CharField(max_length = 100)
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255, blank=True)
    cover_id = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='want')
    notes = models.TextField(blank=True)
    rating = models.IntegerField(null=True, blank=True)

    def cover_url(self):
        if self.cover_id:
            return f"https://covers.openlibrary.org/b/id/{self.cover_id}-M.jpg"
        return ""
    
    def __str__(self):
        return self.title