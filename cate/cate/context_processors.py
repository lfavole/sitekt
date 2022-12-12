from django.http import HttpRequest

def app_name(request: HttpRequest):
    return {"app": request.resolver_match.app_name}
