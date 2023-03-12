import ftplib


def upload_file_to_destination(destination, file, filename):
    """ Upload a file to this FTP destination """
    ftp_kwargs = {
        "host": destination.host,
    }
    for field, kwarg in [
        ("username", "user"),
        ("password", "passwd"),
        ("custom_timeout", "timeout"),
    ]:
        value = getattr(destination, field, None)
        if value:
            ftp_kwargs[kwarg] = value
    ftp_connection = ftplib.FTP(**ftp_kwargs)
    if destination.directory:
        ftp_connection.cwd(destination.directory)
    ftp_connection.storbinary(f"STOR {filename}", file)
    ftp_connection.quit()
    return f"{destination.url_prefix}{filename}"
