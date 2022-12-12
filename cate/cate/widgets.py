from django import forms

class MarkdownEditor(forms.Textarea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "html-editor"

    class Media:
        css = {
            "all": (
               "/static/codemirror/codemirror.css",
            )
        }
        js = (
            "/static/codemirror/codemirror.js",
            "/static/codemirror/codemirror-markdown.js",
            "/static/codemirror/codemirror-mdn-like.css",
            "/static/codemirror/codemirror-xml.js",
            "/static/codemirror/codemirror-init.js",
        )
