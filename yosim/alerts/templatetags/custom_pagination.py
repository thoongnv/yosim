# -*- coding: utf-8 -*-
from django import template

register = template.Library()


@register.filter(name="get_paging_list")
def get_paging_list(value, curr_page_num):
    """
        Return a list of pages which skip pages in the middle
        Use: {% for a in value_list|get_paging_list:curr_page_num %}
    """
    num_of_pages_per_side = 7      # num pages in the left or right
    num_of_pages = len(value)       # length of value
    new_value = []

    if num_of_pages <= 20:
        return value

    closest_curr_page = [x for x in range(
        curr_page_num - 2, curr_page_num + 3) if x >= 0]
    default_left_value = list(range(1, num_of_pages_per_side + 1))
    default_right_value = list(range(
        num_of_pages - num_of_pages_per_side, num_of_pages + 1))

    if curr_page_num <= num_of_pages // 2:
        left_value = []
        if closest_curr_page[-1] > num_of_pages_per_side:
            left_value = list(range(1, len(closest_curr_page) + 1))
            left_value += closest_curr_page
        else:
            left_value = default_left_value
        new_value = left_value + ['skip'] + default_right_value
    else:
        right_value = []
        if closest_curr_page[0] >= (num_of_pages - num_of_pages_per_side):
            right_value = default_right_value
        else:
            right_value = closest_curr_page
            right_value += list(range(
                num_of_pages - len(closest_curr_page), num_of_pages + 1))
        new_value = default_left_value + ['skip'] + right_value

    return new_value
