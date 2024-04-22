from django.db import models


class CloudTrailRecord(models.Model):
    UserName = models.CharField(max_length=30)
    EventName = models.CharField(max_length=50)
    UserAgent = models.CharField(max_length=200)
    ResourceName = models.CharField(max_length=200)
    ResourceType = models.CharField(max_length=200)
    EventTime = models.DateTimeField()
    sourceIPAddr = models.GenericIPAddressField()
    RequestParameters = models.CharField(max_length=2000, blank=True)

    def __str__(self):
        return f"{self.EventName} by {self.UserName} on {self.EventTime}"

    class Meta:
        abstract = True


class CloudTrailCndevRecord(CloudTrailRecord):
    class Meta:
        db_table = "cloudtrailcndev"
        app_label = "cloudtrailapp"


class CloudTrailCnprodRecord(CloudTrailRecord):
    class Meta:
        db_table = "cloudtrailcnprod"
        app_label = "cloudtrailapp"


class CloudTrailCn09Record(CloudTrailRecord):
    class Meta:
        db_table = "cloudtrailcn09"
        app_label = "cloudtrailapp"
