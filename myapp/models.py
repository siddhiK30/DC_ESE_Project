from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class GuestbookEntry(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_entries')
    recipients = models.ManyToManyField(User, related_name='received_entries')
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)  # Optional: to track if entry has been read

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Entry by {self.sender.username} at {self.created_at}"
