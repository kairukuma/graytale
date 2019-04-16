from django import template

register = template.Library()

def subhead(sub):
    return sub.name.lower()[0].capitalize()

def subneck(sub):
    if len(sub.name.lower()) > 1:
        return sub.name.lower()[1]

    return ''

register.filter(subhead)
register.filter(subneck)