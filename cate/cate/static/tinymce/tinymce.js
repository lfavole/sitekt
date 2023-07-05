(function() {
	return;
	var $ = django.jQuery;

	function setTheme(theme) {
		$(".tox.tox-tinymce").each(function(index, value) {
			var editor = tinymce.get(value.id);
		});
	}

	var setItem = localStorage.setItem.bind(localStorage);
	localStorage.setItem = function(key, value) {
		setItem(key, value);
		if(key == "theme") {
			if(value == "auto")
				setTheme(window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
			else
				setTheme(value);
		}
	};
	setTheme(localStorage.getItem("theme"));
})();