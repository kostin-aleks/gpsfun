

def atoi(value, default=None):
    try:
        rc = int(value)
    except (ValueError, TypeError):
        rc = default
    return rc
            

