from django import template

register = template.Library()

@register.simple_tag
def define(value = None):
	return value

@register.simple_tag
def define_list(*args):
	return args

class Addable(list):
    def __add__(self, other):
        self.append(other)
        return self

    def __radd__(self, other):
        obj = self.copy()
        self.clear()
        self.append(other)
        self.extend(obj)
        return self

@register.simple_tag
def define_addable(*args):
	return Addable(args)
