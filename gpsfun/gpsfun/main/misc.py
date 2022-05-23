"""
misc utils
"""

def atoi(value, default=None):
    """ return integer from string or None """
    try:
        result = int(value)
    except (ValueError, TypeError):
        result = default
    return result
