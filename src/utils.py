def merge(*dicts):
    """Merges the given dictionaries into a single dictionary, ignoring overlapping keys."""

    out = dict()
    for dictionary in dicts:
        for (key, val) in dictionary.items():
            out[key] = val
    return out