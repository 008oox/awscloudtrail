from django.http import HttpResponse
import sys, json, time
from pathlib import Path

current_file_directory = Path(__file__).resolve().parent
want_directory = current_file_directory.parent.parent
sys.path.append(str(want_directory))

from Save import SettleAPI as SetAPI

from .utils import render_Str_Name
from django.shortcuts import render
from .models import CloudTrailRecord
from django.views.decorators.csrf import csrf_exempt
from .GetCloudTrail import getCloudTrail
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def GetRecord():
    session = SetAPI.SettleAPI.getSession("cndev")
    End = int(time.time()) - 310
    # timestamp should be pushed forward 5 mins, as in AWS cloudtrail records will be synced per 5 mins
    Start = getCloudTrail.Sync_time(End)
    UserList = getUserList(session)
    processed_events_list = []

    def get_combined_resource_values(resources, key):
        if resources:
            return ", ".join(resource.get(key, "") for resource in resources)
        else:
            return "-"

    try:
        for Dict in UserList:
            User = Dict["UserName"]
            all_events = getCloudTrail.LookupEvents(session, "Username", User, Start, End)
            filtered_events = [event for event in all_events if event.get("EventName") != "LookupEvents"]
            for record in filtered_events:
                cloudTrailEvt = json.loads(record["CloudTrailEvent"])
                record["CloudTrailEvent"] = cloudTrailEvt
                output = {
                    "UserName": record["Username"],
                    "EventName": record["EventName"],
                    "UserAgent": record["CloudTrailEvent"]["userAgent"][:200],
                    "EventTime": record["EventTime"],
                    "ResourceType": get_combined_resource_values(record["Resources"], "ResourceType")[:200],
                    "ResourceName": get_combined_resource_values(record["Resources"], "ResourceName")[:200],
                    "sourceIPAddr": record["CloudTrailEvent"]["sourceIPAddress"],
                }
                print(output)
                if len(processed_events_list) > 0:
                    LastRecord = processed_events_list[-1]
                    if (LastRecord.get("EventName") != output.get("EventName")) or (LastRecord.get("UserName") != output.get("UserName")):
                        processed_events_list.append(output)
                else:
                    processed_events_list.append(output)

    except Exception as e:
        getCloudTrail.Sync_time(Start)
        raise e

    return processed_events_list[::-1]


@csrf_exempt
def update_data(request):
    if request.method == "POST":
        try:
            aws_data = GetRecord()
            for data in aws_data:
                CloudTrailRecord.objects.create(**data)
            return JsonResponse({"message": "Data updated successfully."})
        except Exception as e:
            return JsonResponse({"error_message": f"Error updating data: {e}"})

    return render({"message": ""})


def getUserList(session):
    IAM = session.client("iam")
    UserList = IAM.list_users()["Users"]
    return UserList


def cloudtrail_records(request):
    username_filter = ""
    eventname_filter = ""
    resourcetype_filter = ""
    resourcename_filter = ""
    sourceipaddr_filter = ""
    useragent_filter = ""

    if request.method == "POST":
        username_filter = request.POST.get("UserName", "")
        eventname_filter = request.POST.get("EventName", "")
        resourcetype_filter = request.POST.get("ResourceType", "")
        resourcename_filter = request.POST.get("ResourceName", "")
        sourceipaddr_filter = request.POST.get("sourceIPAddr", "")
        useragent_filter = request.POST.get("UserAgent", "")

        request.session["username_filter"] = username_filter
        request.session["eventname_filter"] = eventname_filter
        request.session["resourcetype_filter"] = resourcetype_filter
        request.session["resourcename_filter"] = resourcename_filter
        request.session["sourceipaddr_filter"] = sourceipaddr_filter
        request.session["useragent_filter"] = useragent_filter

    else:
        username_filter = request.session.get("username_filter", "")
        eventname_filter = request.session.get("eventname_filter", "")
        resourcetype_filter = request.session.get("resourcetype_filter", "")
        resourcename_filter = request.session.get("resourcename_filter", "")
        sourceipaddr_filter = request.session.get("sourceipaddr_filter", "")
        useragent_filter = request.session.get("useragent_filter", "")

    filters = {}
    if username_filter:
        filters["UserName__icontains"] = username_filter
    if eventname_filter:
        filters["EventName__icontains"] = eventname_filter
    if resourcetype_filter:
        filters["ResourceType__icontains"] = resourcetype_filter
    if resourcename_filter:
        filters["ResourceName__icontains"] = resourcename_filter
    if sourceipaddr_filter:
        filters["sourceIPAddr__icontains"] = sourceipaddr_filter
    if useragent_filter:
        filters["UserAgent__icontains"] = useragent_filter

    records = CloudTrailRecord.objects.filter(**filters).order_by("EventTime")
    items_per_page = 200
    paginator = Paginator(records, items_per_page)
    page_number = int(request.GET.get("page", 1))

    try:
        page_records = paginator.page(page_number)
    except PageNotAnInteger:
        page_records = paginator.page(1)
    except EmptyPage:
        page_records = paginator.page(paginator.num_pages)

    return render(
        request,
        "cloudtrail_records.html",
        {
            "page_records": page_records,
            "username_filter": username_filter,
            "eventname_filter": eventname_filter,
            "resourcetype_filter": resourcetype_filter,
            "resourcename_filter": resourcename_filter,
            "sourceipaddr_filter": sourceipaddr_filter,
            "useragent_filter": useragent_filter,
        },
    )


def index(request):
    session = SetAPI.SettleAPI.getSession("cndev")
    UserList = getUserList(session)
    User = render_Str_Name(UserList)
    return HttpResponse(User)
    # return HttpResponse(f"User List:<br>{User}", content_type="text/html")
