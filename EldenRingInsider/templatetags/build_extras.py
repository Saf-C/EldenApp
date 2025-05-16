# EldenRingInsider/templatetags/build_extras.py
from django import template

register = template.Library()

@register.filter
def get_slot(slots, slot_code):
    return slots.filter(slot_name=slot_code).first()
