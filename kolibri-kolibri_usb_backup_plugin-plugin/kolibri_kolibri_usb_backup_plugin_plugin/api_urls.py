from django.urls import re_path
from .views import some_api_function

urlpatterns = [
    re_path(r"^backup/$", some_api_function, name="backup_api"),
]