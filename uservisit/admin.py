from django.contrib import admin

class UserVisitAdmin(admin.ModelAdmin):
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

	def has_add_permission(self, request, obj = None):
		return False
	def has_change_permission(self, request, obj = None):
		return False
	def has_delete_permission(self, request, obj = None):
		return False
