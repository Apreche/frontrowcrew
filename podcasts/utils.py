def seconds_to_timespan(seconds=0):
    """
    Convert a number of seconds into Normal Play time
    https://www.w3.org/TR/media-frags/#naming-time
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    output = ""
    if hours:
        output += f"{hours}:"
    if hours or minutes:
        output += f"{minutes:02}:"
    output += f"{seconds:02}"
    return output

def milliseconds_to_timespan(milliseconds=0):
    seconds = round(milliseconds / 1000)
    return seconds_to_timespan(seconds)