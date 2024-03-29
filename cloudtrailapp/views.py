import json

from .GetRecordFromAWS import GetRecordFromAWS
from .ViewModels import cloudtrailByUser, QueryResource

from .utils import render_Str_Name
from django.shortcuts import render
from .models import CloudTrailCndevRecord, CloudTrailCnprodRecord

from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


Table = {"cndev": CloudTrailCndevRecord, "cnprod": CloudTrailCnprodRecord}


def GetRecordByUser(ENV):
    return GetRecordFromAWS.GetRecordFromAwsByUser.GetRecordsByUser(ENV=ENV)


@csrf_exempt
def update_data(request, ENV):
    if request.method == "POST":
        try:
            aws_data = GetRecordByUser(ENV=ENV)
            for Listdata in aws_data:
                for data in Listdata:
                    Table[ENV].objects.create(**data)
            return JsonResponse({"message": "Data updated successfully."})
        except Exception as e:
            return JsonResponse({"error_message": f"Error updating data: {e}"})

    return HttpResponse(json.dumps({"message": ""}), content_type="application/json")


def cloudtrail_records(request, ENV):
    (
        page_records,
        username_filter,
        eventname_filter,
        resourcetype_filter,
        resourcename_filter,
        sourceipaddr_filter,
        useragent_filter,
        RequestParameters_filter,
    ) = cloudtrailByUser.get_cloudtrail_records_all(request=request, ENV=ENV, Table=Table)
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
