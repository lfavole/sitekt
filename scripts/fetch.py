import os
import sys

PYTHONANYWHERE = os.environ.get("PYTHONANYWHERE_SITE", "") != ""

if not PYTHONANYWHERE:
	sys.exit()

USERNAME = os.environ.get("USERNAME", "")

FOLDER = "/home/" + USERNAME + "/django-cate/cate"
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)
os.chdir(FOLDER)

os.system("git init")
os.system("git pull https://github.com/lfavole/django-cate.git")
os.system("python manage.py migrate")
os.system("python manage.py collectstatic --no-input")
print("OK")
