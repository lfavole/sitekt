from typing import Callable

try:
    import minify_html
except ImportError:
    minify_html = None
from django.http import HttpRequest, HttpResponse


class MinifyHtmlMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if self.should_minify(request, response):
            content = response.content.decode(response.charset)
            try:
                content = minify_html.minify(  # type: ignore
                    content,
                    minify_css=True,
                    minify_js=True,
                )
            except:
                return response
            response.content = content
            if "Content-Length" in response:
                response["Content-Length"] = len(response.content)
        return response

    def should_minify(self, request: HttpRequest, response: HttpResponse) -> bool:
        return (
            bool(minify_html)
            and not getattr(response, "streaming", False)
            and (request.resolver_match is None or getattr(request.resolver_match.func, "should_minify_html", True))
            and response.get("Content-Encoding", "") == ""
            and response.get("Content-Type", "").split(";", 1)[0] == "text/html"
        )
