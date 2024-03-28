from django.db.models import Count, F, Q
from ..forms import DateRangeForm


def Resource_Filter(request, ENV, Table):
    form = DateRangeForm(request.POST or None)
    resource_stats = []

    if request.method == "POST" and form.is_valid():
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        NameKey = form.cleaned_data.get("UserName", "")
        EventKey = form.cleaned_data.get("EventName", "")
        ResourceTypeKey = form.cleaned_data.get("ResourceType", "")
        ResourceNameKey = form.cleaned_data.get("ResourceName", "")
        RequestParametersKey = form.cleaned_data.get("RequestParameters", "")

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
            .filter(RequestParameters__icontains=RequestParametersKey)
            .exclude(Q(EventName__icontains="Get") | Q(EventName__icontains="Describe") | Q(ResourceType="-"))
            .values("UserName", "EventName", "EventTime", "ResourceType", "ResourceName", "RequestParameters", "sourceIPAddr")
        )

    return form, resource_stats
