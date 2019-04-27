from django import template

register = template.Library()

def subhead(sub):
    #return sub['name'].lower()[0].capitalize()
    return sub['topic'].lower()[0].capitalize()

def subneck(sub):
    if len(sub['topic'].lower()) > 1:
        return sub['topic'].lower()[1]

    return ''

def notified(topic):
    if topic['notification']:
        return ''
    return 'hidden'

register.filter(notified)
register.filter(subhead)
register.filter(subneck)