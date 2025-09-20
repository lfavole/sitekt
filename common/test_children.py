import datetime as dt
from urllib.parse import urlparse

from common.test_utils import REMOVED, DefaultArgs, TestCase, clean
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Child

webpage_def_args = DefaultArgs(
    {
        "nom": "FAVOLE",
        "prenom": "Laurent",
        "date_naissance": dt.date(2000, 1, 1),
        "lieu_naissance": "X",
        "adresse": "...",
        "code_postal_ville": "...",
        "ecole": "PASTEUR",
        "classe": "CM2",
        "bapteme": True,
        "date_bapteme": dt.date(2000, 7, 1),
        "lieu_bapteme": "X",
        "premiere_communion": True,
        "date_premiere_communion": dt.date(2009, 6, 1),
        "lieu_premiere_communion": "X",
        "profession": False,
        "date_profession": None,
        "lieu_profession": "",
        "confirmation": False,
        "date_confirmation": None,
        "lieu_confirmation": "",
        "nom_pere": "A",
        "adresse_pere": "",
        "code_postal_ville_pere": "",
        "tel_pere": "0607080910",
        "email_pere": "abc@gmail.com",
        "nom_mere": "B",
        "adresse_mere": "",
        "code_postal_ville_mere": "",
        "tel_mere": "0605040302",
        "email_mere": "def@gmail.com",
        "freres_soeurs": "",
        "autres_infos": "",
        "photos": True,
        "frais": 35,
    }
)
def_args = DefaultArgs(
    {
        **webpage_def_args,
        "communion_cette_annee": False,
        "profession_cette_annee": False,
        "confirmation_cette_annee": False,
        "paye": False,
        "signe": False,
    }
)


class ChildsTests(TestCase):
    """
    Tests on childs.
    """

    def test_subscription_page(self):
        """
        The subscription page requires login
        """
        response = self.client.get(reverse("inscription"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.url).path.rstrip("/"), reverse("account_login").rstrip("/"))

    def test_subscription_page_logged_in(self):
        """
        The subscription page works correctly when logged in
        """
        user = get_user_model().objects.create_user("lfavole")
        self.client.force_login(user)

        response = self.client.get(reverse("inscription"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Inscription")

    def test_confirmation_page(self):
        """
        The confirmation page does not requires login
        """
        response = self.client.get(reverse("inscription_ok"))
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.text, "<h1>.*?Inscription.*?</h1>")
        self.assertContains(response, "Votre inscription a bien été enregistrée.")

    def test_confirmation_page_logged_in(self):
        """
        The confirmation page works correctly when logged in
        """
        user = get_user_model().objects.create_user("lfavole")
        self.client.force_login(user)

        response = self.client.get(reverse("inscription_ok"))
        self.assertEqual(response.status_code, 200)
        self.assertRegex(response.text, "<h1>.*?Inscription.*?</h1>")
        self.assertContains(response, "Votre inscription a bien été enregistrée.")

    def test_webpage(self):
        """
        Subscription on the webpage
        """
        user = get_user_model().objects.create_user("lfavole")
        self.client.force_login(user)

        response = self.client.post(reverse("inscription_nouveau"), webpage_def_args(post=True))
        self.assertIsInstance(response, HttpResponseRedirect)
        child = Child.objects.all()[0]
        self.assertEqual(response["Location"], reverse("inscription_ok_pk", args=(child.pk,)))

        childs = list(Child.objects.all())
        self.assertEqual(len(childs), 1)
        child = childs[0]

        for key, value in def_args().items():
            self.assertTrue(hasattr(child, key), f"The attribute {key} should exist")
            self.assertEqual(getattr(child, key), value)

    def test_normal(self):
        """
        Normal child
        """
        args = def_args()
        child = Child(**args)
        with self.assertValidationOK():
            clean(child)

        for key, value in args.items():
            self.assertTrue(hasattr(child, key), f"The attribute {key} should exist")
            self.assertEqual(getattr(child, key), value)
