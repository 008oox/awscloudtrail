import os, sys, time, json
from datetime import datetime

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
sys.path.append(current_dir)
SaveDirectory = os.path.abspath(os.path.join(current_file_path, "../../../"))
sys.path.append(SaveDirectory)
from Save import SettleAPI as SetAPI
from GetRecordFromAWS.GetCloudTrail import getCloudTrail


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'awscloudtrail.settings')

import django
django.setup()
from cloudtrailapp.models import CloudTrailCndevRecord, CloudTrailCnprodRecord, CloudTrailCn09Record, CloudTrailCn01Record

class GetRecordFromAwsByUser:
    def GetRecordsByUser(ENV, start_time=None, end_time=None):
        session = GetRecordFromAwsByUser.GetSession(ENV)

        if end_time is None:
            end_time = int(time.time()) - 310
        if start_time is None:
            start_time = getCloudTrail.Sync_time(end_time, ENV)
        
        UserList = GetRecordFromAwsByUser.getUserList(session)
        processed_events_list, all_processed_events = [], []

        def get_combined_resource_values(resources, key):
            if resources:
                return ", ".join(resource.get(key, "") for resource in resources)
            else:
                return "-"

        try:
            for Dict in UserList:
                User = Dict["UserName"]
                all_events = getCloudTrail.LookupEvents(session, "Username", User, start_time, end_time)
                filtered_events = [
                    event for event in all_events 
                    if event.get("EventName") != "LookupEvents" and 
                    "List" not in event.get("EventName", "") and
                    "Describe" not in event.get("EventName", "")]
                for record in filtered_events:
                    cloudTrailEvt = json.loads(record["CloudTrailEvent"])
                    record["CloudTrailEvent"] = cloudTrailEvt
                    request_parameters = cloudTrailEvt.get("requestParameters")
                    output = {
                        "UserName": record["Username"],
                        "EventName": record["EventName"],
                        "UserAgent": record["CloudTrailEvent"]["userAgent"][:200],
                        "EventTime": record["EventTime"],
                        "ResourceType": get_combined_resource_values(record["Resources"], "ResourceType")[:200],
                        "ResourceName": get_combined_resource_values(record["Resources"], "ResourceName")[:200],
                        "sourceIPAddr": record["CloudTrailEvent"]["sourceIPAddress"],
                        "RequestParameters": json.dumps(request_parameters) if request_parameters else "-",
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
            getCloudTrail.Sync_time(start_time)
            raise e

        return all_processed_events[::-1]

    def getUserList(session):
        IAM = session.client("iam")
        UserList = IAM.list_users()["Users"]
        return UserList

    def GetSession(ENV):
        return SetAPI.SettleAPI.getSession(ENV)



def to_unix_time(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())

start_date = "2025-01-21 05:00:25"
end_date = "2025-02-05 06:27:03"
#end_date = "2024-12-04 15:21:03"
custom_start_time = to_unix_time(start_date)
custom_end_time = to_unix_time(end_date)

ENV='cndev'

aws_data = GetRecordFromAwsByUser.GetRecordsByUser(ENV, start_time=custom_start_time, end_time=custom_end_time)


Table = {
    "cndev": CloudTrailCndevRecord,
    "cnprod": CloudTrailCnprodRecord,
    "cn09": CloudTrailCn09Record,
    "cn01": CloudTrailCn01Record
}

def insert_data_to_db(aws_data, ENV):
    try:
        model = Table.get(ENV)
        if not model:
            raise ValueError(f"Model for ENV '{ENV}' not found.")

        for Listdata in aws_data:
            for data in Listdata:
                model.objects.create(**data)

        print(f"Data successfully inserted into the {ENV} table.")

    except Exception as e:
        print(f"Error inserting data: {e}")

insert_data_to_db(aws_data, ENV)
