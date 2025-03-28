import json, time
import logging
from .GetRecordFromAWS import GetRecordFromAWS
from .ViewModels import cloudtrailByUser, QueryResource

from .utils import render_Str_Name
from django.shortcuts import render, redirect
from .models import CloudTrailCndevRecord, CloudTrailCnprodRecord, CloudTrailCn09Record, CloudTrailCn01Record

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


Table = {"cndev": CloudTrailCndevRecord, "cnprod": CloudTrailCnprodRecord, "cn09": CloudTrailCn09Record, "cn01": CloudTrailCn01Record}


def GetRecordByUser(ENV):
    return GetRecordFromAWS.GetRecordFromAwsByUser.GetRecordsByUser(ENV=ENV)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@csrf_exempt
def update_data(request, ENV):
    if request.method == "POST":
        try:
            count = 0
            aws_data = GetRecordByUser(ENV=ENV)
            batch_size = 50
            batch = []
            for data in aws_data:
                batch.append(Table[ENV](**data))
                if len(batch) >= batch_size:
                    Table[ENV].objects.bulk_create(batch)
                    batch.clear()
                    count += batch_size
                    time.sleep(1)
            if batch:
                count += len(batch)
                Table[ENV].objects.bulk_create(batch)                
            return JsonResponse({"message": "Data in all %d updated successfully." % count})
        except Exception as e:
            logging.error(f"Error updating data: {e}", exc_info=True)
            return JsonResponse({"error_message": f"Error updating data: {e}"})

    return HttpResponse(json.dumps({"message": ""}), content_type="application/json")

def cloudtrail_records(request, ENV):
    username_filter = request.POST.get("UserName", "") or request.session.get("username_filter", "")
    eventname_filter = request.POST.get("EventName", "") or request.session.get("eventname_filter", "")
    resourcetype_filter = request.POST.get("ResourceType", "") or request.session.get("resourcetype_filter", "")
    resourcename_filter = request.POST.get("ResourceName", "") or request.session.get("resourcename_filter", "")
    sourceipaddr_filter = request.POST.get("sourceIPAddr", "") or request.session.get("sourceipaddr_filter", "")
    useragent_filter = request.POST.get("UserAgent", "") or request.session.get("useragent_filter", "")
    RequestParameters_filter = request.POST.get("RequestParameters", "") or request.session.get("RequestParameters_filter", "")

    if request.method == "POST":
        request.session["username_filter"] = username_filter
        request.session["eventname_filter"] = eventname_filter
        request.session["resourcetype_filter"] = resourcetype_filter
        request.session["resourcename_filter"] = resourcename_filter
        request.session["sourceipaddr_filter"] = sourceipaddr_filter
        request.session["useragent_filter"] = useragent_filter
        request.session["RequestParameters_filter"] = RequestParameters_filter

    page_records, username_filter, eventname_filter, resourcetype_filter, resourcename_filter, sourceipaddr_filter, useragent_filter, RequestParameters_filter = cloudtrailByUser.get_cloudtrail_records_all(
        request=request, ENV=ENV, Table=Table
    )

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
            "RequestParameters_filter": RequestParameters_filter,
            "ENV": ENV,
        },
    )

def resource_view(request, ENV):
    form, resource_stats = QueryResource.Resource_Filter(request=request, ENV=ENV, Table=Table)
    return render(
        request,
        "resource.html",
        {"form": form, "resource_stats": resource_stats, "ENV": ENV},
    )


def index(request, ENV):
    session = GetRecordFromAWS.GetRecordFromAwsByUser.GetSession(ENV)
    UserList = GetRecordFromAWS.GetRecordFromAwsByUser.getUserList(session)
    User = render_Str_Name(UserList)
    return HttpResponse(User)
    # return HttpResponse(f"User List:<br>{User}", content_type="text/html")
