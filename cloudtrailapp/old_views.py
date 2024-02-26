from django.http import HttpResponse
import sys
from pathlib import Path

current_file_directory = Path(__file__).resolve().parent
want_directory = current_file_directory.parent.parent
sys.path.append(str(want_directory))

from Save import SettleAPI as SetAPI

from .utils import render_Str_Name
from django.shortcuts import render
from .models import CloudTrailRecord


def monitoring_report(request):
    cloudtrail_data = [
        {"UserName": "user1", "EventName": "Login", "EventType": "SignIn", "EventTime": "2023-01-01 10:00:00", "sourceIPAddr": "192.168.1.1"},
    ]
    for record_info in cloudtrail_data:
        CloudTrailRecord.objects.create(
            UserName=record_info["UserName"],
            EventName=record_info["EventName"],
            EventType=record_info["EventType"],
            EventTime=record_info["EventTime"],
            sourceIPAddr=record_info["sourceIPAddr"],
        )

    cloudtrail_records = CloudTrailRecord.objects.all()

    context = {
        "cloudtrail_data": cloudtrail_records,
    }

    return render(request, "monitoring_report.html", context)


def index(request):
    session = SetAPI.SettleAPI.getSession("cndev")
    IAM = session.client("iam")
    UserList = IAM.list_users()["Users"]

    User = render_Str_Name(UserList)

    return HttpResponse(User)
    # return HttpResponse(f"User List:<br>{User}", content_type="text/html")
