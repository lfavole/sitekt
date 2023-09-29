import datetime as dt

from common.test_utils import REMOVED, DefaultArgs, TestCase, clean
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
        "ecole": "PASTEUR",
        "classe": "CM2",
        "redoublement": False,
        "annees_evf": 4,
        "annees_kt": 3,
        "bapteme": True,
        "date_bapteme": dt.date(2000, 7, 1),
        "lieu_bapteme": "X",
        "pardon": True,
        "annee_pardon": 2009,
        "premiere_communion": True,
        "date_premiere_communion": dt.date(2009, 6, 1),
        "lieu_premiere_communion": "X",
        "nom_pere": "A",
        "adresse_pere": "",
        "tel_pere": "0607080910",
        "email_pere": "abc@gmail.com",
        "nom_mere": "B",
        "adresse_mere": "",
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
        **webpage_def_args.dict,
        "communion_cette_annee": False,
    }
)


class ChildsTests(TestCase):
    """
    Tests on childs.
    """

    def test_subscription_page(self):
        """
        The subscription page works correctly
        """
        response = self.client.get(reverse("espacecate:inscription"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Inscription")

    def test_confirmation_page(self):
        """
        The confirmation page works correctly
        """
        response = self.client.get(reverse("espacecate:inscription_ok"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Inscription")
        self.assertContains(response, "Votre inscription a bien été enregistrée.")

    def test_webpage(self):
        """
        Subscription on the webpage
        """
        args = webpage_def_args()
        response = self.client.post(reverse("espacecate:inscription"), args)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertEqual(response["Location"], reverse("espacecate:inscription_ok"))

        childs = list(Child.objects.all())
        self.assertEqual(len(childs), 1)
        child = childs[0]

        for key, value in args.items():
            self.assertTrue(hasattr(child, key), f"The attribute {key} doesn't exist")
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
            self.assertTrue(hasattr(child, key), f"The attribute {key} doesn't exist")
            self.assertEqual(getattr(child, key), value)
