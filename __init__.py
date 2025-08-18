# Make functions available at package level
from .custom_functions import get_snippets, extract_phone_numbers, visit_and_extract_phone_info

__all__ = ['get_snippets', 'extract_phone_numbers', 'visit_and_extract_phone_info']
