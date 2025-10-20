def truncate_string(s, max_length=100):
    return s[:min(max_length, len(s))]