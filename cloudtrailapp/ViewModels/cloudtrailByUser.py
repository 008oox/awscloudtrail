from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_cloudtrail_records_all(request, ENV, Table):
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

    return page_records, username_filter, eventname_filter, resourcetype_filter, resourcename_filter, sourceipaddr_filter, useragent_filter
