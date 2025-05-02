# from django.db import models
# from django.contrib.auth.models import User
# from django.utils import timezone

# class GuestbookEntry(models.Model):
#     sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_entries')
#     recipients = models.ManyToManyField(User, related_name='received_entries')
#     content = models.TextField()
#     created_at = models.DateTimeField(default=timezone.now)
#     is_read = models.BooleanField(default=False)  # Optional: to track if entry has been read

#     class Meta:
#         ordering = ['-created_at']

#     def __str__(self):
#         return f"Entry by {self.sender.username} at {self.created_at}"
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class GuestbookEntry(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_entries')
    recipients = models.ManyToManyField(User, related_name='received_entries')
    content = models.TextField()
    
    # Original timestamp fields
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    
    # New timestamp fields for Berkeley Clock synchronization
    synchronized_timestamp = models.DateTimeField(null=True, blank=True)
    sender_local_time = models.DateTimeField(null=True, blank=True)
    time_offset = models.FloatField(null=True, blank=True, help_text="Offset in seconds from coordinator time")
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Entry by {self.sender.username} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # If synchronized_timestamp is not set, use created_at
        if not self.synchronized_timestamp:
            self.synchronized_timestamp = self.created_at
            
        super().save(*args, **kwargs)