from typing import Any

from .models import Page

def navbar_processor(request):
	pages_list = Page.objects.filter(hidden = False)

	def get_pages(parent):
		pages_query = pages_list.filter(parent_page = parent)
		pages: list[tuple[Page, Any]] = []
		for page in pages_query:
			pages.append((page, get_pages(page)))
		return pages

	return {"pages": get_pages(None)}
