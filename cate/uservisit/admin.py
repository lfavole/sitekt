from django.contrib import admin


class CommonUserVisitAdmin(admin.ModelAdmin):
	"""
	Admin interface for user visits.
	"""
	list_display = ("timestamp", "session_key", "remote_addr", "user_agent")
	list_filter = ("timestamp",)
	search_fields = ("ua_string",)
	readonly_fields = (
		"hash",
		"timestamp",
		"session_key",
		"remote_addr",
		"user_agent",
		"ua_string",
		"namespace",
		"view",
	)
	ordering = ("-timestamp",)

	def has_add_permission(self, _request, _obj = None):
		return False
	def has_change_permission(self, _request, _obj = None):
		return False
	def has_delete_permission(self, _request, _obj = None):
		return False
