import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse

from .models import Article

now = datetime.datetime(2023, 1, 1, 12, 0, 0)
one_day = datetime.timedelta(days=1)


class ArticlesTests(TestCase):
    """
    Tests on the articles.
    """

    def test_no_articles(self):
        """
        No articles => "Aucun article" in the list page
        """
        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun article")
        self.assertQuerysetEqual(response.context["articles"], [])

    def test_one_article(self):
        """
        An article is shown in the list
        """
        article = Article.objects.create(title="Test article", content="The content of the article...", date=now)

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)
        self.assertQuerysetEqual(response.context["articles"], [article])

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 200)

    def test_hidden_article(self):
        """
        A hidden article isn't shown in the list
        """
        article = Article.objects.create(
            title="Test article", content="The content of the article...", date=now, hidden=True
        )

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun article")
        self.assertQuerysetEqual(response.context["articles"], [])

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 404)

    def test_future_article(self):
        """
        A future article isn't shown in the list
        """
        article = Article.objects.create(
            title="Test article", content="The content of the article...", date=datetime.datetime.now() + one_day
        )

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun article")
        self.assertQuerysetEqual(response.context["articles"], [])

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 404)

    def prepare_user(self):
        user = get_user_model().objects.create_user("lfavole")
        # view_articles = Permission.objects.get(name="Can view article")
        view_articles = Permission.objects.get_by_natural_key("view_article", "espacecate", "article")
        user.user_permissions.add(view_articles)
        self.client.force_login(user)

    def test_admin_hidden_article(self):
        """
        The admins can see the hidden articles.
        They are displayed in the list with "Article caché" message.
        """
        self.prepare_user()
        article = Article.objects.create(title="Test article", content="The content of the article...", hidden=True)

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article caché")

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.content)

    def test_admin_empty_article(self):
        """
        The admins can see the empty articles in the list with "Article vide" message.
        """
        self.prepare_user()
        article = Article.objects.create(title="Test article", content="")

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article vide")

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)

    def test_admin_future_article(self):
        """
        The admins can see the future articles in the list with "Article futur" message.
        """
        self.prepare_user()
        article = Article.objects.create(
            title="Test article", content="The content of the article...", date=datetime.datetime.now() + one_day
        )

        response = self.client.get(reverse("espacecate:articles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Article futur")

        response = self.client.get(resolve_url(article))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.content)
