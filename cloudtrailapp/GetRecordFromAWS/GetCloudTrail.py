import json, sys, time, os
from datetime import datetime

# sys.path.append(r"d:\Work\CQC\aws_ops")
current_file_path = os.path.abspath(__file__)
SaveDirectory = os.path.abspath(os.path.join(current_file_path, "../../../../"))
timestamp_path = os.path.abspath(os.path.join(current_file_path, "../.."))
sys.path.append(SaveDirectory)


from Save import SettleAPI as SetAPI

# import datetrans as datetrans


class getCloudTrail:
    def lookupCloudEvents(cloudTrail, key, keyvalue, StartTime, EndTime, next_token=None):
        lookup_attributes = [{"AttributeKey": key, "AttributeValue": keyvalue}]
        lookup_params = {"LookupAttributes": lookup_attributes, "MaxResults": 50, "StartTime": StartTime, "EndTime": EndTime}

        if next_token:
            lookup_params["NextToken"] = next_token

        return cloudTrail.lookup_events(**lookup_params)

    def LookupEvents(Session, key, keyvalue, Start, End):
        ##/ https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudtrail/client/lookup_events.html
        cloudtrail = Session.client("cloudtrail")
        StartTime = datetime.utcfromtimestamp(Start)
        EndTime = datetime.utcfromtimestamp(End)
        all_events = []
        next_token = None
        while True:
            ListEvent = getCloudTrail.lookupCloudEvents(cloudtrail, key, keyvalue, StartTime, EndTime, next_token)
            all_events.extend(ListEvent["Events"])
            if "NextToken" in ListEvent:
                next_token = ListEvent["NextToken"]
            else:
                break

        return all_events

    def Sync_time(End, ENV):
        File_path = os.path.join(timestamp_path, "timeStamp", "Last" + ENV + ".txt")
        with open(File_path, "r") as File:
            Content = File.read()
            Start = int(Content) if Content else 1707000000
        with open(File_path, "w") as File:
            File.write(str(End))
        return Start

    def main():
        session = SetAPI.SettleAPI.getSession("cndev")
        End = int(time.time()) - 300
        # AWS will update in CloudTrail per 5 mins
        Start = getCloudTrail.Sync_time(End)
        print(Start)
        all_events = getCloudTrail.LookupEvents(session, "Username", "king.chen", Start, End)
        filtered_events = [event for event in all_events if event.get("EventName") != "LookupEvents"]
        for record in filtered_events:
            cloudTrailEvt = json.loads(record["CloudTrailEvent"])
            record["CloudTrailEvent"] = cloudTrailEvt
            ##/ python allow <record['CloudTrailEvent']> call var 'cloudTrailEvt', it will call a Json format value of  <'CloudTrailEvent'>
            output = json.dumps(record, indent=4, cls=datetrans.ComplexEncoder)
            print(output)


if __name__ == "__main__":
    getCloudTrail = getCloudTrail
    getCloudTrail.main()
