from django.db import models


class CloudTrailRecord(models.Model):
    UserName = models.CharField(max_length=30)
    EventName = models.CharField(max_length=50)
    UserAgent = models.CharField(max_length=200, default="-")
    EventType = models.CharField(max_length=30)
    EventTime = models.DateTimeField()
    sourceIPAddr = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.EventName} by {self.UserName} on {self.EventTime}"

    class Meta:
        db_table = "cloudtrailrecord"
