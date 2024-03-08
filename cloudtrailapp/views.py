from django.http import HttpResponse
import sys, json, time
from pathlib import Path

current_file_directory = Path(__file__).resolve().parent
want_directory = current_file_directory.parent.parent
sys.path.append(str(want_directory))

from Save import SettleAPI as SetAPI

from .utils import render_Str_Name
from django.shortcuts import render
from .models import CloudTrailCndevRecord, CloudTrailCnprodRecord
from django.views.decorators.csrf import csrf_exempt
from .GetCloudTrail import getCloudTrail
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Q
from .forms import DateRangeForm


Table = {"cndev": CloudTrailCndevRecord, "cnprod": CloudTrailCnprodRecord}


def GetRecord(ENV):
    session = SetAPI.SettleAPI.getSession(ENV)
    End = int(time.time()) - 310
    # timestamp should be pushed forward 5 mins, as in AWS cloudtrail records will be synced per 5 mins
    Start = getCloudTrail.Sync_time(End, ENV)
    UserList = getUserList(session)
    processed_events_list, all_processed_events = [], []

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

                if len(processed_events_list) >= 10000:
                    all_processed_events.append(tuple(processed_events_list[::-1]))
                    processed_events_list.clear()

        all_processed_events.append(tuple(processed_events_list[::-1]))

    except Exception as e:
        getCloudTrail.Sync_time(Start)
        raise e

    return all_processed_events[::-1]
    # return processed_events_list[::-1]


@csrf_exempt
def update_data(request, ENV):
    if request.method == "POST":
        try:
            aws_data = GetRecord(ENV)
            for Listdata in aws_data:
                for data in Listdata:
                    Table[ENV].objects.create(**data)
            return JsonResponse({"message": "Data updated successfully."})
        except Exception as e:
            return JsonResponse({"error_message": f"Error updating data: {e}"})

    return HttpResponse(json.dumps({"message": ""}), content_type="application/json")


def getUserList(session):
    IAM = session.client("iam")
    UserList = IAM.list_users()["Users"]
    return UserList


def cloudtrail_records(request, ENV):
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

    records = Table[ENV].objects.filter(**filters).order_by("EventTime")
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
        "cloudtrailrecords.html",
        {
            "page_records": page_records,
            "username_filter": username_filter,
            "eventname_filter": eventname_filter,
            "resourcetype_filter": resourcetype_filter,
            "resourcename_filter": resourcename_filter,
            "sourceipaddr_filter": sourceipaddr_filter,
            "useragent_filter": useragent_filter,
            "ENV": ENV,
        },
    )


def resource_view(request, ENV):
    form = DateRangeForm(request.POST or None)
    resource_stats = []

    if request.method == "POST" and form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        NameKey = form.cleaned_data.get("UserName", "")
        EventKey = form.cleaned_data.get("EventName", "")
        ResourceTypeKey = form.cleaned_data.get("ResourceType", "")
        ResourceNameKey = form.cleaned_data.get("ResourceName", "")

        resource_stats = (
            Table[ENV]
            .objects.filter(
                EventTime__date__gte=start_date,
                EventTime__date__lte=end_date,
            )
            .filter(UserName__icontains=NameKey)
            .filter(EventName__icontains=EventKey)
            .filter(ResourceType__icontains=ResourceTypeKey)
            .filter(ResourceName__icontains=ResourceNameKey)
            .exclude(Q(EventName__icontains="Get") | Q(EventName__icontains="Describe") | Q(ResourceType="-"))
            .values("UserName", "EventName", "UserAgent", "EventTime", "ResourceType", "ResourceName", "sourceIPAddr")
            # .annotate(resource_count=Count("ResourceType"))
            # .filter(resource_count__gt=0)
        )

    return render(
        request,
        "resource.html",
        {"form": form, "resource_stats": resource_stats, "ENV": ENV},
    )


def index(request):
    session = SetAPI.SettleAPI.getSession("cndev")
    UserList = getUserList(session)
    User = render_Str_Name(UserList)
    return HttpResponse(User)
    # return HttpResponse(f"User List:<br>{User}", content_type="text/html")
