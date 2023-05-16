from django import forms


class DatalistWidget(forms.widgets.Select):
    """
    Widget for `<datalist>`.
    """
    template_name = "widgets/datalist.html"

    def optgroups(self, *args, **kwargs):
        print(f"optgroups {args=}")
        print(f"optgroups {kwargs=}")
        ret = super().optgroups(*args, **kwargs)
        print(f"optgroups {ret=}")
        return ret

class DatalistFormField(forms.ChoiceField, forms.CharField):
    """
    Text field with `<datalist>`.
    """
    widget = DatalistWidget
    def __init__(self, *args, choices = (), **kwargs) -> None:
        choices = [(choice, choice) for choice in choices]
        super().__init__(*args, **kwargs)
        attrs = self.widget.attrs
        attrs |= self.widget_attrs(self.widget) # type: ignore
        self.widget = DatalistWidget({**self.widget.attrs, **self.widget_attrs(self.widget)}, choices) # type: ignore

    def valid_value(self, _value):
        return True
