import datetime
import mimetypes
from pathlib import Path
from typing import Any, Literal, Optional, Type
from urllib.parse import quote, urlencode
from django.conf import settings
from django.db import models

from allauth.account.models import EmailAddress
from django.contrib.auth import get_permission_codename
from django.contrib.auth.decorators import login_required
from django.contrib.messages import add_message
from django.contrib.messages.constants import INFO
from django.db.models import Model
from django.db.models.fields.files import FieldFile
from django.db.models.query_utils import Q
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseNotModified
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import content_disposition_header, http_date
from django.utils.timezone import now
from django.views import generic
from django.views.static import was_modified_since
from icalendar import Alarm, Calendar as ICalendar, Event

from .forms import SubscriptionForm
from .models import (
    Article,
    Child,
    Date,
    DateCategory,
    Document,
    DocumentCategory,
    LastChildVersion,
    OldChild,
    Page,
    Year,
)
from .pdfs.authorization import Authorization
from .pdfs.calendar import Calendar
from .pdfs.dates_list import DatesList

autorisation = Authorization.as_view("")
calendar = Calendar.as_view("")
dates_list = DatesList.as_view("")


def _encode_filename(filename: str):
    try:
        filename.encode("ascii")
        return 'filename="{}"'.format(filename.replace("\\", "\\\\").replace('"', r"\""))
    except UnicodeEncodeError:
        return "filename*=utf-8''{}".format(quote(filename))


def link_children(request):
    """
    Link unlinked children that don't have a user to a user if a verified email matches.
    """
    children = LastChildVersion.objects.filter(user=None)
    email_addresses = EmailAddress.objects.filter(user=request.user)
    for child in children:
        for email in email_addresses:
            if any(
                email_to_try == email.email
                for email_to_try in (child.email_jeune, child.email_mere, child.email_pere)
            ):
                child.user = request.user
                child.save()
                add_message(request, INFO, f"Enfant {child} lié à votre compte.")
                break


@login_required
def subscription(request):
    link_children(request)

    emails = EmailAddress.objects.filter(user=request.user)
    children = LastChildVersion.objects.filter(user=request.user, year__lt=Year.get_current())
    registered_children = LastChildVersion.objects.filter(user=request.user, year=Year.get_current())

    return render(
        request,
        "common/subscription.html",
        {
            "emails": emails,
            "children": children,
            "registered_children": registered_children,
            "year": Year.get_current(),
        },
    )


def subscription_ok(request, pk=None):
    child = None
    if pk:
        child = get_object_or_404(Child, user=request.user, pk=pk)
    return render(request, "common/subscription_ok.html", {"child": child})


def subscription_old(request, pk):
    child = get_object_or_404(OldChild.objects.filter(user=request.user), id=pk)
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            new_child = form.save(request)
            return redirect("inscription_ok_pk", new_child.pk)
    else:
        old_class = Child.Classes(child.classe)
        try:
            child.classe = (Child.Classes(child.classe) + (Year.get_current() - child.year)).value
        except IndexError:
            child.classe = Child.Classes.AUTRE

        if old_class.changed_school(Child.Classes(child.classe)):
            child.ecole = None
        form = SubscriptionForm(child.__dict__)

    return render(request, "common/subscription_old.html", {"child": child, "form": form})


def subscription_new(request):
    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            new_child = form.save(request)
            return redirect("inscription_ok_pk", new_child.pk)
    else:
        form = SubscriptionForm()
    return render(request, "common/subscription_new.html", {"form": form})


class Occurrence:
    def __init__(self, event: Date):
        self.event = event

    @property
    def start(self) -> datetime.date | datetime.datetime:
        return self.event.start

    @property
    def end(self) -> datetime.date | datetime.datetime:
        return self.event.end


def dates_ics(request):
    categories = DateCategory.objects.all()
    categories_query = [category for category in request.GET.get("categories", "").split(",") if category]
    if categories_query:
        categories = categories.filter(slug__in=categories_query)
    occurrences = [
        Occurrence(date)
        for date
        in Date.objects.filter(categories__in=categories).distinct()
    ]

    now = datetime.datetime.now()

    cal = ICalendar()
    cal.calendar_name = (
        "Toutes les dates"
        if not categories_query
        else ", ".join(category.title for category in categories)
    )
    cal.description = cal.calendar_name
    cal.add("PRODID", f"-//Secteur paroissial de l'Embrunais et du Savinois//Espace caté {Year.get_current().formatted_year} (https://github.com/lfavole/sitekt)//")
    cal.add("VERSION", "2.0")
    cal.add("X-WR-CALNAME", cal.calendar_name)
    cal.add("X-WR-CALDESC", cal.calendar_name)

    for i, occurrence in enumerate(occurrences, start=1):
        event = Event()
        event.add("summary", occurrence.event.name)
        event.add("DTSTAMP", now)
        event.uid = f"{occurrence.event.pk}_{i}"
        event.start = occurrence.start

        # Default to 1 hour duration, will not trigger on all-day events (1 hour < 1 day)
        event.end = occurrence.end or occurrence.start + datetime.timedelta(hours=1)

        # Add place info
        if occurrence.event.place:
            event.add("location", occurrence.event.place)

        # Add reminders
        # Reminder 1: 1 day before at 5 PM
        alarm1 = Alarm()
        alarm1.add("action", "DISPLAY")
        alarm1.add("description", f'"{occurrence.event.name}" commence demain' + (f" à {occurrence.start.time()}" if isinstance(occurrence.start, datetime.datetime) else ""))
        # 1 day before at 5 PM
        alarm1.TRIGGER = datetime.datetime.combine(occurrence.start, datetime.time(17, 0, 0)) - datetime.timedelta(days=1)
        event.add_component(alarm1)

        # Reminder 2: 15 minutes before (only if not an all-day event)
        if isinstance(occurrence.start, datetime.datetime):
            alarm2 = Alarm()
            alarm2.add("action", "DISPLAY")
            alarm2.add("description", f'"{occurrence.event.name}" commence dans 15 minutes')
            # 15 minutes before
            alarm2.add("trigger", occurrence.start - datetime.timedelta(minutes=15))
            event.add_component(alarm2)

        cal.add_component(event)

    # Include active site messages as all-day events for today + next 6 days
    try:
        site_messages = SiteMessage.objects.filter(is_active=True)
    except Exception:
        site_messages = []

    emoji_map = {
        "DEBUG": "🐞",
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❗",
    }

    today = datetime.date.today()
    for msg in site_messages:
        prefix = emoji_map.get(msg.level, "ℹ️") + " "
        for delta in range(7):
            day = today + datetime.timedelta(days=delta)
            event = Event()
            summary = prefix + msg.message
            event.add("summary", summary)
            event.add("DTSTAMP", now)
            event.uid = f"site_message_{msg.pk}_{day.isoformat()}"
            # all-day event: start date, end date = next day
            event.start = day
            event.end = day + datetime.timedelta(days=1)
            cal.add_component(event)

    cal.add_missing_timezones()

    # Add filename
    return HttpResponse(
        cal.to_ical(),
        content_type="text/calendar",
        headers={
            "Content-Disposition": content_disposition_header(
                True,
                "dates_" + now.strftime("%Y%m%d_%H%M%S") + ".ics"
            ),
        },
    )


def has_permission_for_view(view: generic.View, permission="view"):
    return has_permission(view.request, view.model, permission)  # type: ignore


def has_permission(request: HttpRequest, model: Type[Model], permission="view"):
    perm_name = model._meta.app_label + "." + get_permission_codename(permission, model._meta)
    return request.user.has_perm(perm_name)  # type: ignore


class BaseView(generic.View):
    """
    Base view with template and queryset selection.
    """

    context_object_name: str
    template_filename: str
    model: Type[Model]

    def get_queryset(self, nav=False):  # pylint: disable=C0116
        admin = has_permission_for_view(self, "view")
        ret = self.model.objects.all()
        if not admin:
            content_or_url = Q()
            if hasattr(self.model, "content"):
                # always display the homepage because it has a template when empty
                content_or_url |= ~Q(content="")
            if nav and hasattr(self.model, "url"):
                content_or_url |= ~Q(url="")
            has_child_pages = Q(child_pages__isnull=False) if hasattr(self.model, "child_pages") and nav else Q()
            is_homepage = Q(slug=Page.HOME_TEMPLATE.slug) if hasattr(self.model, "slug") else Q()
            ret = ret.filter(content_or_url | has_child_pages | is_homepage)
            if hasattr(self.model, "hidden"):
                ret = ret.filter(hidden=False)
            if hasattr(self.model, "date"):
                ret = ret.filter(date__lte=now())
        ret = ret.distinct()  # https://stackoverflow.com/a/38452675
        return ret

    @property
    def extra_context(self):  # pylint: disable=C0116
        return {"app": self.request.resolver_match.app_name}


def redirect_to_home(request):
    return redirect("page", slug=Page.HOME_TEMPLATE.slug)


class PageView(BaseView, generic.DetailView):
    """
    View for a page.
    """

    model = Page
    context_object_name = "page"
    template_name = "common/page.html"

    def get_object(self, *args, **kwargs):
        try:
            ret = super().get_object(*args, **kwargs)
        except Http404:
            # If there's no homepage, return the homepage template
            slug = self.kwargs.get(self.slug_url_kwarg)
            if slug != Page.HOME_TEMPLATE.slug:
                raise
            return Page.HOME_TEMPLATE
        return ret


class ArticleListView(BaseView, generic.ListView):
    """
    View for an article list.
    """

    model = Article
    context_object_name = "articles"
    template_name = "common/articles.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return {
            **super().get_context_data(**kwargs),
            "article_view": self.request.resolver_match.view_name.replace("articles", "article", 1),
        }


class ArticleView(BaseView, generic.DetailView):
    """
    View for an article.
    """

    model = Article
    context_object_name = "article"
    template_name = "common/article.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        return {
            **super().get_context_data(**kwargs),
            "article_list_view": self.request.resolver_match.view_name.replace("article", "articles", 1),
        }


class DateListView(BaseView, generic.ListView):
    """
    View for a date list.
    """

    model = Date
    context_object_name = "dates"
    template_name = "common/dates.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("categories")

    def get_context_data(self, **kwargs):
        ret = super().get_context_data(**kwargs)
        ret["categories"] = DateCategory.objects.all()
        return ret


class DocumentListView(BaseView, generic.ListView):
    """
    View for an document list.
    """

    model = Document
    context_object_name = "docs"
    template_name = "common/docs.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("categories")

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        ret: dict[Literal[""] | DocumentCategory, list[Document]] = {"": []}

        obj: Document
        cat: DocumentCategory
        for obj in self.object_list:  # type: ignore
            added = False
            for cat in obj.categories.all():
                if cat not in ret:
                    ret[cat] = []
                ret[cat].append(obj)
                added = True

            if not added:
                ret[""].append(obj)

        kwargs["docs_ordered"] = ret

        return kwargs


def serve(request, obj: Document | FieldFile | Path | str):
    """
    Return a response that serves a file.
    """
    if isinstance(obj, Document):
        obj = obj.file
    try:
        if isinstance(obj, FieldFile):
            obj = obj.path
    except NotImplementedError:
        # no absolute paths
        return redirect(obj.url)

    fullpath = Path(obj)

    # Respect the If-Modified-Since header.
    statobj = fullpath.stat()
    if not was_modified_since(request.META.get("HTTP_IF_MODIFIED_SINCE"), statobj.st_mtime):
        return HttpResponseNotModified()
    content_type, encoding = mimetypes.guess_type(str(fullpath))
    content_type = content_type or "application/octet-stream"
    response = FileResponse(fullpath.open("rb"), as_attachment=True, content_type=content_type)
    response.headers["Last-Modified"] = http_date(statobj.st_mtime)
    if encoding:
        response.headers["Content-Encoding"] = encoding
    return response


def serve_document(request, pk):
    return serve(request, get_object_or_404(Document, pk=pk))
