from django import template
register = template.Library()

@register.filter(name='access')
def access(value, arg):
    return value[arg]

@register.filter(name='do_the_first')
def do_the_first(value, arg):
	if arg == 1:
		return value
	else:
		return ''