import string
from random import choice


def get_password(size=8):
    safe_letters = ''.join([s for s in string.letters + string.digits if s not in 'liIoO01'])
    return ''.join([choice(safe_letters) for i in range(size)])


def get_readable_password(size=8):
    import re
    chars = string.letters + string.digits
    chars = re.sub('[liI10oO]', '', chars)
    return ''.join([choice(chars) for i in range(size)])
