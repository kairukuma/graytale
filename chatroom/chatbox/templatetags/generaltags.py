from django import template
import validators

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

def validate_post_url(post):
    if (validators.url(post.url)):
        return post.url
    else:
        return 'g/%s/%d' % (post.topic.name,post.id)

def validate_post_external(post):
    if (validators.url(post.url)):
        return '_blank'
    else:
        return ''

register.filter(validate_post_url)
register.filter(validate_post_external)
register.filter(notified)
register.filter(subhead)
register.filter(subneck)