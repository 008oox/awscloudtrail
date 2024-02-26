# awscloudtrail
1. create a mysql DB server

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
