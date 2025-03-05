import os, sys, time, json, logging
from .GetCloudTrail import getCloudTrail

current_file_path = os.path.abspath(__file__)
SaveDirectory = os.path.abspath(os.path.join(current_file_path, "../../../../"))
sys.path.append(SaveDirectory)
from Save import SettleAPI as SetAPI

logger = logging.getLogger('cloudtrailapp')

class GetRecordFromAwsByUser:
    def GetRecordsByUser(ENV):
        session = GetRecordFromAwsByUser.GetSession(ENV)
        End = int(time.time()) - 310
        # timestamp should be pushed forward 5 mins, as in AWS cloudtrail records will be synced per 5 mins
        Start = getCloudTrail.Sync_time(End, ENV)
        UserList = GetRecordFromAwsByUser.getUserList(session)

        def get_combined_resource_values(resources, key):
            if resources:
                return ", ".join(resource.get(key, "") for resource in resources)
            else:
                return "-"

        try:
            logger.info(f"Processing {len(UserList)} users' CloudTrail events")
            total_events = 0
            for Dict in UserList:
                User = Dict["UserName"]
                logger.debug(f"Processing events for user: {User}")
                all_events = getCloudTrail.LookupEvents(session, "Username", User, Start, End)
                for record in all_events:
                    if record.get("EventName") != "LookupEvents":
                        cloudTrailEvt = json.loads(record["CloudTrailEvent"])
                        record["CloudTrailEvent"] = cloudTrailEvt
                        request_parameters = cloudTrailEvt.get("requestParameters", {})
                        output = {
                            "UserName": record.get("Username"),
                            "EventName": record.get("EventName"),
                            "UserAgent": record["CloudTrailEvent"].get("userAgent")[:200],
                            "EventTime": record.get("EventTime"),
                            "ResourceType": get_combined_resource_values(record.get("Resources"), "ResourceType")[:200],
                            "ResourceName": get_combined_resource_values(record.get("Resources"), "ResourceName")[:200],
                            "sourceIPAddr": record["CloudTrailEvent"].get("sourceIPAddress"),
                            "RequestParameters": json.dumps(request_parameters) if request_parameters else "-",
                        }
                        total_events += 1
                        yield output
                        
            logger.info("Completed processing for ENV: %s, total events processed: %d", ENV, total_events)

        except Exception as e:
            logger.error(f"Error occurred while processing records for ENV: {ENV}", exc_info=True)
            getCloudTrail.Sync_time(Start)
            raise e

    def getUserList(session):
        IAM = session.client("iam")
        UserList = IAM.list_users()["Users"]
        return UserList

    def GetSession(ENV):
        return SetAPI.SettleAPI.getSession(ENV)
