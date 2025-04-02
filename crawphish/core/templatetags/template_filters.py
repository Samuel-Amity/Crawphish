# from django import template
# import os

# register = template.Library()

# @register.filter
# def lookup(value, key):
#     if isinstance(value, dict):
#         return value.get(key)
#     return None
# @register.filter
# def basename(value):
#     return os.path.basename(value)