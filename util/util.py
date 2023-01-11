def number(x):
    # it may be already int or float
    if isinstance(x, (int, float)):
        return x
    # all int like strings can be converted to float so int tries first
    try:
        return int(x)
    except (TypeError, ValueError):
        pass
    try:
        return float(x)
    except (TypeError, ValueError):
        return None
