import base64
import datetime as dt
from functools import total_ordering
import hashlib
import mimetypes
import re
from typing import Any, Callable, Type
from urllib.parse import urlparse
import warnings
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from django.apps import apps
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import DatabaseError, models
from django.db.models import Manager
from django.db.utils import NotSupportedError
from django.urls import NoReverseMatch, reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from cate import settings
from storage.fields import FileField, ImageField

from cate.utils.text import slugify

from .fields import DatalistField, PriceField


class YearManager(models.Manager):
    def get_by_natural_key(self, start_year: int) -> "Year":
        return self.get_or_create(start_year=start_year)[0]


class Year(models.Model):
    """
    A school year to be linked to childs, etc.

    It can be active (or not).
    """

    objects = YearManager()

    start_year = models.fields.IntegerField(_("start year"), unique=True)
    is_active = models.fields.BooleanField(_("active year"))

    class Meta:
        verbose_name = _("school year")
        verbose_name_plural = _("school years")
        ordering = ["-start_year"]

    def _get_end_year(self):
        return self.start_year + 1

    _get_end_year.short_description = _("End year")
    end_year = property(_get_end_year)

    def _get_formatted_year(self):
        return f"{self.start_year}-{self.end_year}"

    _get_formatted_year.short_description = _("School year")  # type: ignore
    formatted_year = property(_get_formatted_year)

    def __str__(self):
        return _("School year %s") % (self.formatted_year,)

    def natural_key(self) -> tuple[int]:
        return (self.start_year,)

    def save(self, *args, **kwargs):
        # Note: we avoid saving the objects to avoid recursion error
        obj = type(self).objects.all()
        if self.is_active:
            # this year becomes an active year => deactivate the other years
            for year in obj.filter(is_active=True):
                if year == self:
                    continue
                if not year.is_active:
                    continue  # avoid hitting the database
                year.is_active = False
                year.save()

        elif not obj.filter(is_active=True).exists():
            # no active years => activate the first year or this year
            first = obj.first()
            if first and not first.is_active:  # activate the first year
                first.is_active = True
                first.save()
            else:  # one year => this year is active
                self.is_active = True

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        obj = type(self).objects.all()
        if not obj.filter(is_active=True).exists():
            years = obj.filter(is_active=False)
            if years.exists():
                el = years[0]
                if not el.is_active:  # activate the first year
                    # we avoid saving the objects to avoid recursion error
                    el.is_active = True
                    el.save()
            # we are deleting the only active year
            # there will be bugs...

        return super().delete(*args, **kwargs)

    @classmethod
    def get_current(cls, save=False):
        """
        Return the current year.
        """
        year = cache.get("current_year")
        if not year:
            try:
                year = cls.objects.get(is_active=True)
            except (cls.DoesNotExist, DatabaseError):
                ret = Year(start_year=dt.date.today().year, is_active=True)
                if save:
                    ret.save()
                else:
                    warnings.warn("No active Year object. Creating a fake object")
                return ret
            cache.set("current_year", year)
        return year

    @classmethod
    def get(cls, start_year: int, save=False):
        """
        Return the year with the given start year.
        """
        year = cache.get(f"year_{start_year}")
        if not year:
            try:
                year = cls.objects.get(start_year=start_year)
            except (cls.DoesNotExist, DatabaseError):
                ret = Year(start_year=dt.date.today().year,)
                if save:
                    ret.save()
                else:
                    warnings.warn(f"No Year object starting in {start_year}. Creating a fake object")
                return ret
            cache.set(f"year_{start_year}", year)
        return year

    @classmethod
    def get_current_pk(cls):
        return cls.get_current(True).pk

    @property
    def trs(self):
        return [self.tr1, self.tr2, self.tr3]

    @property
    def tr1(self):
        return (dt.date(self.start_year, 9, 1), dt.date(self.end_year, 1, 1))

    @property
    def tr2(self):
        return (dt.date(self.end_year, 1, 1), dt.date(self.end_year, 4, 1))

    @property
    def tr3(self):
        return (dt.date(self.end_year, 4, 1), dt.date(self.end_year, 7, 1))

    def __sub__(self, other):
        if isinstance(other, int):
            return Year.get(self.start_year - other)
        return self.start_year - other.start_year

    def __add__(self, other):
        return Year.get(self.start_year + other)


class HasSlugManager(models.Manager):
    def get_by_natural_key(self, slug: str) -> "HasSlug":
        return self.get(slug=slug)


class HasSlug(models.Model):
    """
    Base class for models that have a slug.
    """

    objects = HasSlugManager()

    slug = models.fields.SlugField(_("slug"), max_length=100, unique=True, editable=False)
    title = models.fields.CharField(_("title"), max_length=100)

    class Meta:
        abstract = True

    def _generate_slug(self, try_slugs=True):
        value = self.title
        slug_candidate = slug_original = slugify(value)
        if not try_slugs:
            return slug_candidate

        i = 0
        while True:
            i += 1
            if not type(self).objects.filter(slug=slug_candidate).exists():  # type: ignore
                break
            slug_candidate = slug_original + "-" + str(i)

        return slug_candidate

    def save(self, *args, **kwargs):
        if self._state.adding and not self.slug:
            self.slug = self._generate_slug()

        super().save(*args, **kwargs)

    def __str__(self):  # pylint: disable=E0307
        return self.title

    def natural_key(self) -> tuple[str]:
        return (self.slug,)


class PageBase(HasSlug):
    """
    Base class for pages and articles.
    """

    content = models.fields.TextField(_("content"), blank=True)
    hidden = models.fields.BooleanField(_("hidden page"), default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        self._write_base64_images()

    def _write_base64_images(self):
        """
        Creates the corresponding objects for Base64 images in the page/article.
        Saves the element only if needed.
        """
        edited = False

        soup = BeautifulSoup(self.content)
        for i, img in enumerate(soup.find_all("img")):
            if not (src := img.attrs.get("src")):
                continue

            if (parse_result := urlparse(src)).scheme != "data":
                continue

            mimetype, data = parse_result.path.split(",", 1)
            if mimetype.endswith(";base64"):
                mimetype = mimetype.removesuffix(";base64")
                data = base64.b64decode(data)

            if not (ext := mimetypes.guess_extension(mimetype)):
                continue

            if not (path := self._save_image(f"blobid{i}{ext}", data)):
                continue
            img.attrs["src"] = path

            edited = True

        if edited:
            self.content = soup.prettify()
            super().save()

    def _save_image(self, filename, content):
        """
        Saves the image with the corresponding filename and content.
        Returns the URL.
        """
        Image: Type[ImageBase] = apps.get_model(self._meta.app_label, self._meta.model_name + "Image")  # type: ignore
        image_obj = Image.objects.create(page=self, image=ContentFile(content, filename))
        return image_obj.image.url

    def __str__(self):  # pylint: disable=E0307
        return self.title


class ImageBase(models.Model):
    """
    Base class for images in pages and articles.
    """

    image = ImageField(_("image"))
    page: "models.ForeignKey[Page]"

    def __str__(self):
        return _("Image '%s' in %s") % (self.image.url, self.page)

    class Meta:
        abstract = True


class Page(PageBase):
    """
    A page.
    """

    order = models.PositiveIntegerField(_("order"), default=0, null=False)
    parent_page = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("Previous page"),
        related_name="parent_pages",
    )

    class Meta:
        verbose_name = _("page")
        ordering = ["order"]

    def get_absolute_url(self):
        if self.content == "":
            return "#"

        if len(self.content) < 100 and self.content[0] != "<":
            try:
                return reverse(self.content)
            except NoReverseMatch:
                pass

        return reverse("page", kwargs={"slug": self.slug})


class PageImage(ImageBase):
    """
    An image on a page.
    """

    page = models.ForeignKey(Page, on_delete=models.CASCADE, verbose_name=_("Page"))

    class Meta:
        verbose_name = _("page image")
        verbose_name_plural = _("page images")


class Article(PageBase):
    """
    Common article class for all apps.
    """

    date = models.fields.DateField(_("date"), default=now)
    hidden = models.fields.BooleanField(_("hidden article"), default=False)

    @property
    def thumbnail_url(self):
        match = re.search(r"youtube.com/embed/([a-zA-Z0-9_-]+)", self.content)
        if match:
            return f"https://i.ytimg.com/vi/{match.group(1)}/mqdefault.jpg"

        return None

    @property
    def gradient(self):
        hash = hashlib.md5(self.title.encode()).digest()
        angle = int.from_bytes(hash) % 360
        first_color = int.from_bytes(hash[:4]) % 256
        second_color = int.from_bytes(hash[4:8]) % 256
        return f"linear-gradient({angle}deg, #{first_color:06x}, #{second_color:06x})"

    class Meta:
        verbose_name = _("article")
        ordering = ["-date"]


class ArticleImage(ImageBase):
    """
    Common article image class for all apps.
    """

    page = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_("Article"))

    class Meta:
        verbose_name = _("article image")
        verbose_name_plural = _("article images")


class GroupManager(models.Manager):
    def get_by_natural_key(self, name: str) -> "Group":
        return self.get_or_create(name=name)[0]


class Group(models.Model):
    """
    Common group class for all apps.
    """

    objects = GroupManager()

    name = models.fields.CharField(_("name"), max_length=100, unique=True)
    app = models.fields.CharField(_("app"), max_length=100, blank=True)
    classes = models.fields.TextField(
        _("classes"), blank=True, help_text=_("Classes that can be in this group")
    )

    def __str__(self):
        return self.name

    def natural_key(self) -> tuple[str]:
        return (self.name,)

    class Meta:
        verbose_name = _("group")


@total_ordering
class ClassesMixin:
    """Common methods to the `Classes` enums."""
    order = ["PS", "MS", "GS", "CP", "CE1", "CE2", "CM1", "CM2", "6eme", "5eme", "4eme", "3eme", "2nde", "1ere", "terminale"]

    def __lt__(self, other):
        return self.order.index(self.value) < self.order.index(other.value)

    def __getitem__(self, index):
        if isinstance(index, int):
            return type(self)(self.order[index])
        return super().__getitem__(index)

    def __add__(self, count):
        return type(self)(self.order[self.order.index(self.value) + count])

    def __sub__(self, other):
        if isinstance(other, type(self)):
            return self.order.index(self.value) - self.order.index(other.value)
        return type(self)(self.order[self.order.index(self.value) - other])

    def changed_school(self, other):
        """Return `True` if the child changed school between the two classes, `False` otherwise."""
        groups = [
            ("PS", "MS", "GS"),
            ("CP", "CE1", "CE2", "CM1", "CM2"),
            ("6eme", "5eme", "4eme", "3eme"),
            ("2nde", "1ere", "terminale"),
        ]
        for group in groups:
            if self in group and other in group:
                return False
        return True


class ChildManager(models.Manager):
    """Manager for children. Returns only children for the current year (and the future years)."""
    def get_queryset(self):
        return super().get_queryset().filter(year__start_year__gte=Year.get_current().start_year)

    def get_by_natural_key(self, nom: str, prenom: str, year: int | None = None) -> "Child":
        if year is None:
            year = Year.get_current().start_year
        return self.get(nom=nom, prenom=prenom, year__start_year=year)


class OldChildManager(ChildManager):
    """Manager for old children. Returns only children for the previous years."""
    def get_queryset(self):
        return super(ChildManager, self).get_queryset().filter(year__start_year__lt=Year.get_current().start_year)


class LastVersionManager(ChildManager):
    """Manager for children's last version. Returns the most recent version of a child."""
    def get_queryset(self):
        seen_previous_years = set()
        seen_this_year = set()
        previous_year = None
        pks = []

        for child in super(ChildManager, self).get_queryset().order_by("year"):
            if child.year != previous_year:
                seen_previous_years.update(seen_this_year)
                seen_this_year.clear()

            if (child.nom, child.prenom) not in seen_previous_years:
                pks.append(child.pk)
            seen_this_year.add((child.nom, child.prenom))

            previous_year = child.year

        return super(ChildManager, self).get_queryset().order_by("year").filter(pk__in=pks)


def items_for(app, manager_class=models.Manager):
    class ItemsFor(manager_class):
        def get_queryset(self):
            return super().get_queryset().filter(**({"groupe__app": app} if hasattr(self.model, "groupe") else {}))

    return ItemsFor()


def get_default_group():
    return Group.objects.get_or_create(name="Autre")[0].pk


class Child(models.Model):
    """
    Common child class for all apps.
    """

    class Classes(ClassesMixin, models.TextChoices):
        PS = "PS", "Petite section"
        MS = "MS", "Moyenne section"
        GS = "GS", "Grande section"
        CP = "CP", "CP"
        CE1 = "CE1", "CE1"
        CE2 = "CE2", "CE2"
        CM1 = "CM1", "CM1"
        CM2 = "CM2", "CM2"
        SIXIEME = "6eme", "6ème"
        CINQUIEME = "5eme", "5ème"
        QUATRIEME = "4eme", "4ème"
        TROISIEME = "3eme", "3ème"
        SECONDE = "2nde", "2nde"
        PREMIERE = "1ere", "1ère"
        TERMINALE = "terminale", "Terminale"
        AUTRE = "autre", "Autre"

        def __lt__(self, other):
            return self._sort_order_ < other._sort_order_

    objects = ChildManager()

    nom = models.CharField("Nom de famille", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)
    date_naissance = models.DateField("Date de naissance")
    lieu_naissance = models.CharField("Lieu de naissance", max_length=100)
    adresse = models.TextField("Adresse")
    code_postal_ville = models.CharField("Code postal et ville", max_length=100)
    tel_jeune = models.CharField("Téléphone du jeune", max_length=10, blank=True)
    email_jeune = models.EmailField("Email du jeune", max_length=100, blank=True)

    ecole = models.fields.CharField("École", max_length=100)
    classe = models.fields.CharField("Classe", choices=Classes.choices, max_length=10)

    bapteme = models.fields.BooleanField("Baptême")
    date_bapteme = models.fields.DateField("Date du Baptême", blank=True, null=True)
    lieu_bapteme = models.CharField("Lieu du Baptême", max_length=100, blank=True)

    premiere_communion = models.fields.BooleanField("Première Communion")
    date_premiere_communion = models.fields.DateField("Date de la Première Communion", blank=True, null=True)
    lieu_premiere_communion = models.CharField("Lieu de la Première Communion", max_length=100, blank=True)

    profession = models.fields.BooleanField("Profession de foi")
    date_profession = models.fields.DateField("Date de la Profession de Foi", blank=True, null=True)
    lieu_profession = models.CharField("Lieu de la Profession de Foi", max_length=100, blank=True)

    confirmation = models.fields.BooleanField("Confirmation")
    date_confirmation = models.fields.DateField("Date de la Confirmation", blank=True, null=True)
    lieu_confirmation = models.CharField("Lieu de la Confirmation", max_length=100, blank=True)

    nom_pere = models.CharField("Nom et prénom du père", blank=True, max_length=100)
    adresse_pere = models.TextField("Adresse du père", blank=True)
    code_postal_ville_pere = models.CharField("Code postal et ville du père", blank=True, max_length=100)
    tel_pere = models.CharField("Téléphone du père", blank=True, max_length=10)
    email_pere = models.EmailField("Email du père", blank=True, max_length=100)

    nom_mere = models.CharField("Nom et prénom de la mère", blank=True, max_length=100)
    adresse_mere = models.TextField("Adresse de la mère", blank=True)
    code_postal_ville_mere = models.CharField("Code postal et ville de la mère", blank=True, max_length=100)
    tel_mere = models.CharField("Téléphone de la mère", blank=True, max_length=10)
    email_mere = models.EmailField("Email de la mère", blank=True, max_length=100)

    freres_soeurs = models.TextField("Frères et soeurs", blank=True)

    autres_infos = models.TextField("Autres informations", blank=True)

    photos = models.BooleanField("Publication des photos")
    frais = PriceField("Participation aux frais")

    communion_cette_annee = models.BooleanField("Communion cette année", default=False)
    profession_cette_annee = models.BooleanField("Profession de Foi cette année", default=False)
    confirmation_cette_annee = models.BooleanField("Confirmation cette année", default=False)
    paye = models.BooleanField("Payé", default=False)
    signe = models.BooleanField("Signé", default=False)
    groupe = models.ForeignKey(Group, verbose_name="Groupe", default=get_default_group, on_delete=models.CASCADE)
    year = models.ForeignKey(Year, verbose_name=_("School year"), on_delete=models.CASCADE, default=Year.get_current_pk)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("User"), on_delete=models.SET_NULL, blank=True, null=True)
    photo = ImageField("Photo", blank=True, null=True)
    date_inscription = models.DateTimeField("Date et heure d'inscription", auto_now_add=True)

    class Meta:
        verbose_name = _("child")
        ordering = ["nom", "prenom"]

    @property
    def app(self):
        return self._meta.app_label

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def natural_key(self) -> tuple[str, str, int]:
        return (self.nom, self.prenom, self.year.start_year)

    @property
    def official_name(self):
        return f"{self.nom} {self.prenom}"

    def get_assigned_group(self):
        """Return the group assigned to this child based on their class."""
        groups = Group.objects.all()
        for group in groups:
            if any(self.classe == classe.strip() for classe in group.classes.splitlines()):
                return group
        return get_default_group()

    def has_two_parents(self) -> bool:
        """Return True if the child has two parents, False otherwise."""
        return bool(self.nom_mere and self.nom_pere)

    sacraments_checks: dict[str, str] = {}

    def clean(self):
        today = dt.date.today()
        errors = {}

        def add_error(field, error):
            if field not in errors:
                errors[field] = []
            errors[field].append(error)

        def check_not_future(name: str, msg: str):
            date: "dt.date" | None = getattr(self, name)
            if date and date > today:
                add_error(name, f"{msg.capitalize()} ne doit pas être dans le futur.")

        def check_after_birth(name: str, msg: str):
            date = getattr(self, name)
            if date and date < self.date_naissance:
                add_error(name, f"{msg.capitalize()} doit être après la date de naissance.")

        def check_sacrament(name: str, msg: str):
            if not getattr(self, name):
                return  # the sacrament hasn't been done

            check_not_future(f"date_{name}", f"la date {msg}")
            check_after_birth(f"date_{name}", f"la date {msg}")

        check_not_future("date_naissance", "la date de naissance")
        for name, msg in self.sacraments_checks.items():
            check_sacrament(name, msg)

        for field, msg in {"tel_mere": "de la mère", "tel_pere": "du père"}.items():
            length = len(getattr(self, field))
            if length not in (0, 10):
                add_error(
                    field,
                    f"Le numéro de téléphone {msg} est incorrect (il a {length} chiffre{'s' if length >= 2 else ''}).",
                )

        if errors:
            raise ValidationError(errors)

    fieldsets = [
        (
            "Informations concernant l'enfant / le jeune",
            {
                "fields": (
                    "nom",
                    "prenom",
                    "date_naissance",
                    "lieu_naissance",
                    "adresse",
                    "code_postal_ville",
                    "tel_jeune",
                    "email_jeune",
                )
            },
        ),
        ("École", {"fields": ("ecole", "classe")}),
        (
            "Caté / Aumônerie",
            {
                "fields": (
                    "bapteme",
                    "date_bapteme",
                    "lieu_bapteme",
                    "premiere_communion",
                    "date_premiere_communion",
                    "lieu_premiere_communion",
                    "profession",
                    "date_profession",
                    "lieu_profession",
                    "confirmation",
                    "date_confirmation",
                    "lieu_confirmation",
                )
            },
        ),
        (
            "Coordonnées",
            {
                "fields": (
                    "nom_mere",
                    "adresse_mere",
                    "code_postal_ville_mere",
                    "tel_mere",
                    "email_mere",
                    "nom_pere",
                    "adresse_pere",
                    "code_postal_ville_pere",
                    "tel_pere",
                    "email_pere",
                    "freres_soeurs",
                )
            },
        ),
        ("Autres informations", {"fields": ("autres_infos",)}),
        ("Autorisation", {"fields": ("photos", "frais")}),
        (
            "Espace administrateur",
            {
                "fields": (
                    "communion_cette_annee",
                    "profession_cette_annee",
                    "confirmation_cette_annee",
                    "paye",
                    "signe",
                    "groupe",
                    "year",
                    "user",
                    "photo",
                    "date_inscription",
                )
            },
        ),
    ]


class OldChild(Child):
    """
    Common old child class for all apps.
    """

    objects = OldChildManager()

    class Meta:
        verbose_name = _("old child")
        verbose_name_plural = _("old children")
        proxy = True


class LastChildVersion(Child):
    """
    Common last child version class for all apps.
    """

    objects = LastVersionManager()

    class Meta:
        verbose_name = _("last child version")
        verbose_name_plural = _("last child versions")
        proxy = True


class DateCategory(HasSlug):
    """
    Category for dates.
    """

    order = models.PositiveIntegerField(_("order"), default=0, null=False)

    class Meta:
        verbose_name = _("date category")
        verbose_name_plural = _("date categories")
        ordering = ["order"]


class Date(models.Model):
    start_date = models.fields.DateField(_("start date"))
    end_date = models.fields.DateField(_("end date"), blank=True, null=True)
    start_time = models.fields.TimeField(_("start time"), blank=True, null=True)
    end_time = models.fields.TimeField(_("end time"), blank=True, null=True)
    time_text = DatalistField(
        _("Time (as text)"), max_length=50, blank=True, form_choices=("Journée", "Week-end", "Séjour")
    )
    name = models.fields.CharField(_("name"), max_length=100)
    short_name = models.fields.CharField(_("short name"), max_length=50, blank=True)
    place = models.fields.CharField(_("place"), max_length=100, blank=True)
    cancelled = models.fields.BooleanField(_("cancelled"))
    categories = models.ManyToManyField(
        DateCategory, verbose_name=_("Categories"), blank=True, related_name="dates", related_query_name="date",
    )

    class Meta:
        verbose_name = _("date")
        ordering = ["start_date", "start_time"]

    def clean(self):
        if self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": _("The end date must be after the start date.")})

        if self.end_time and not self.start_time:
            msg = _("The start time must be specified when the end time is specified.")
            raise ValidationError({"start_time": msg})

        if self.end_time and self.start_time > self.end_time:
            raise ValidationError({"end_time": _("The end time must be after the start time.")})

        if self.start_time and self.end_time and self.time_text:
            msg = _("The start time / end time or the time as text must be specified, not both.")
            raise ValidationError({"start_time": msg, "end_time": msg, "time_text": msg})

    @property
    def start(self) -> dt.date | dt.datetime:
        return (
            dt.datetime.combine(self.start_date, self.start_time).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            if self.start_time
            else self.start_date
        )

    @property
    def end(self) -> dt.date | dt.datetime:
        end_date = self.end_date or (
            # entire day (no end time) => end = 1 day after
            self.start_date + dt.timedelta(days=1)
            if self.start_time is None
            else self.start_date
        )
        return (
            dt.datetime.combine(end_date, self.end_time).replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
            if self.end_time
            else end_date
        )

    @property
    def is_past(self):
        if isinstance(self.end, dt.datetime):
            return now() > self.end
        else:
            return now().date() > self.end

    @property
    def is_current(self):
        return not self.is_past and not self.is_future

    @property
    def is_future(self):
        if isinstance(self.start, dt.datetime):
            return now() < self.start
        else:
            return now().date() < self.start

    def __str__(self):  # pylint: disable=E0307
        return self.name


class MeetingManager(models.Manager):
    def get_by_natural_key(self, date: dt.date, kind: str, name: str) -> "Meeting":
        return self.get(date=date, kind=kind, name=name)


class Meeting(models.Model):
    """
    Common meeting class for all apps.
    """

    objects = MeetingManager()

    class Kind(models.TextChoices):
        CATE = "KT", "Rencontre de caté"
        EVF = "EVF", "Rencontre d'éveil à la foi"
        TEMPS_FORT = "TF", "Temps fort"
        MESSE_FAMILLES = "MF", "Messe des familles"
        AUMONERIE_COLLEGE = "A_COL", "Rencontre d'aumônerie (collège)"
        AUMONERIE_LYCEE = "A_LYC", "Rencontre d'aumônerie (lycée)"
        PROFESSION = "PF", "Profession de Foi"
        CONFIRMATION = "CONF", "Confirmation"

    kind = models.CharField(_("kind"), max_length=5, blank=True, choices=Kind.choices)

    date = models.fields.DateField(_("date"))
    name = models.CharField(_("name"), blank=True, max_length=100, help_text=_("Replaces the meeting kind"))

    group = models.ForeignKey(Group, verbose_name=_("group"), related_name="+", related_query_name="+", on_delete=models.CASCADE, default=get_default_group)

    def get_childs(self) -> Manager[Child]:
        """
        Returns the children that are part of this meeting.
        """
        if self.kind == self.Kind.PROFESSION:
            return Child.objects.filter(profession_cette_annee=True)
        if self.kind == self.Kind.CONFIRMATION:
            return Child.objects.filter(confirmation_cette_annee=True)
        groups = {
            self.Kind.EVF: "EVF",
            self.Kind.CATE: "KT",
            self.Kind.TEMPS_FORT: ("EVF", "KT"),
            self.Kind.MESSE_FAMILLES: "",
            self.Kind.AUMONERIE_COLLEGE: "Aumônerie collège",
            self.Kind.AUMONERIE_LYCEE: "Aumônerie lycée",
        }.get(self.kind)
        if groups is None:
            raise ValueError(f"Unknown meeting kind: {self.kind}")
        if groups == "":
            return Child.objects.all()
        if isinstance(groups, str):
            groups = [groups]
        return Child.objects.filter(groupe__name__in=groups)

    def save(self, *args, **kwargs):
        add = self._state.adding
        super().save(*args, **kwargs)
        if add:
            Attendance: Type[CommonAttendance] = apps.get_model(self._meta.app_label, "Attendance")  # type: ignore
            for child in self.get_childs():
                Attendance.objects.create(child=child, meeting=self, is_present=True, has_warned=False)

    def __str__(self):
        return self.name or self.get_kind_display()  # type: ignore

    def natural_key(self) -> tuple[dt.date, str, str]:
        return (self.date, self.kind, self.name)

    class Meta:
        verbose_name = _("meeting")
        ordering = ["date"]


class Attendance(models.Model):
    """
    Common attendance class for all apps.
    """

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        verbose_name=_("Child"),
        blank=True,
        null=True,
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        verbose_name=_("Meeting"),
        blank=True,
        null=True,
    )
    is_present = models.BooleanField(_("present"))
    has_warned = models.BooleanField(_("has warned"))

    def __str__(self):
        return _("%s was %s%s") % (
            str(self.child),
            (
                # Translators: use inclusive writing
                _("present")
                if self.is_present
                # Translators: use inclusive writing
                else _("absent")
            ),
            (" " + _("and has warned")) if self.has_warned else "",
        )

    class Meta:
        verbose_name = _("attendance")


class DocumentCategory(HasSlug):
    """
    Common document category class for all apps.
    """

    order = models.PositiveIntegerField(_("order"), default=0, null=False)

    class Meta:
        verbose_name = _("document category")
        verbose_name_plural = _("document categories")
        ordering = ["order"]


class Document(models.Model):
    """
    Common document class for all apps.
    """

    title = models.fields.CharField(_("document title"), max_length=100)
    file = FileField(_("file"), null=True)
    categories = models.ManyToManyField(DocumentCategory, verbose_name=_("Categories"), blank=True)

    class Meta:
        verbose_name = _("document")

    def __str__(self):  # pylint: disable=E0307
        return self.title
