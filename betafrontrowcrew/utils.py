"""global utils for betafrontrowcrew"""


def str_to_bool(input_string: str) -> bool:
    """ check string for truthiness """
    truthy_strings = ["true", "tru", "t", "y", "yes", "1"]
    return input_string.lower() in truthy_strings
