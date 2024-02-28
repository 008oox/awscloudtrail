# awscloudtrail
0. First we need an access key to login to AWS cloud, for more detail review AWS_setting.read

1. create a mysql DB server, install django, Python:3.9.18, django:4.2.8 , mysql: 8.0

2. config awscloudtrail/settings.py
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": "cloudtrailcndev",
            "USER": "root",
            "PASSWORD": "111111",
            "HOST": "localhost",
            "PORT": "3306",
        }
    }

3. modify cloudtrailapp/models.py

4. database Feature with these fields:
    UserName
    UserAgent
    EventName
    EventType
    EventTime
    sourceIPAddr

5. python manage.py makemigrations

   python manage.py migrate

6. python manage.py runserver

7. http://127.0.0.1:8000/cloudtrailapp/cloudtrail_records/

8. sync to latest use a timestamp location: cloudtrailapp/timeStamp/Lastcndev.txt
    This timestamp is the start timestamp , and when finish syncing timestamp will be replaced to the 
    current.timstamp - 310s

    ![Code Demo](./images/results.gif)