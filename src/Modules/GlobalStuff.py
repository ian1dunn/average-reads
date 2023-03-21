INCREMENT_START_CHAR = '0'
INCREMENT_END_CHAR = 'z'


def increment_chr(c: chr):
    """
    :param c: character to increment
    :return: incremented character of c between start and end char
    """
    return chr(ord(c) + 1) if c != INCREMENT_END_CHAR else INCREMENT_START_CHAR


def increment_str(s: str):
    """
    http://bit.ly/2iJfRou
    :param s: String to increment with characters between start and end char
    :return: Incremented string (z -> 10, zz -> 000)
    """
    lpart = s.rstrip(INCREMENT_END_CHAR)
    num_replacements = len(s) - len(lpart)
    new_s = lpart[:-1] + increment_chr(lpart[-1]) if lpart else INCREMENT_START_CHAR
    new_s += INCREMENT_START_CHAR * num_replacements
    return new_s
