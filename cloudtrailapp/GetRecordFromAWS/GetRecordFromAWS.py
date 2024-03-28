import os, sys, time, json
from .GetCloudTrail import getCloudTrail

current_file_path = os.path.abspath(__file__)
SaveDirectory = os.path.abspath(os.path.join(current_file_path, "../../../../"))
sys.path.append(SaveDirectory)
from Save import SettleAPI as SetAPI


class GetRecordFromAwsByUser:
    def GetRecordsByUser(ENV):
        session = GetRecordFromAwsByUser.GetSession(ENV)
        End = int(time.time()) - 310
        # timestamp should be pushed forward 5 mins, as in AWS cloudtrail records will be synced per 5 mins
        Start = getCloudTrail.Sync_time(End, ENV)
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
                all_events = getCloudTrail.LookupEvents(session, "Username", User, Start, End)
                filtered_events = [event for event in all_events if event.get("EventName") != "LookupEvents"]
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
            getCloudTrail.Sync_time(Start)
            raise e

        return all_processed_events[::-1]

    def getUserList(session):
        IAM = session.client("iam")
        UserList = IAM.list_users()["Users"]
        return UserList

    def GetSession(ENV):
        return SetAPI.SettleAPI.getSession(ENV)
