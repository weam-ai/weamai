import ast
from src.logger.default_logger import logger

def extract_error_message(error_message):
    try:
        # Split the error message to isolate the dictionary part
        dict_str = error_message.split(' - ', 1)[1]
        
        # Convert the string to a dictionary
        error_dict = ast.literal_eval(dict_str)
        
        # Extract the desired message
        error_content = error_dict['error']['message']
        error_code = error_dict['error']['code']
        return error_content,error_code
    
    except Exception as e:
        # Handle exceptions that may occur during extraction
        logger.error(f"Failed to extract error message: {e}")
        return "An unknown error occurred"
    



from datetime import datetime, timezone

def custom_parse_datetime(date_string: str) -> datetime:
    """
    Parses a date_string returned from the server to a datetime object.

    This parser is designed to handle both date strings with and without
    microseconds. It is expected that the server format will remain consistent.

    Example:
        ```py
        > parse_datetime('2022-08-19T07:19:38.123Z')
        datetime.datetime(2022, 8, 19, 7, 19, 38, 123000, tzinfo=timezone.utc)
        > parse_datetime('2022-08-19T07:19:38Z')
        datetime.datetime(2022, 8, 19, 7, 19, 38, tzinfo=timezone.utc)
        ```

    Args:
        date_string (`str`):
            A string representing a datetime returned by the Hub server.
            The string is expected to follow '%Y-%m-%dT%H:%M:%S.%fZ' or '%Y-%m-%dT%H:%M:%SZ' pattern.

    Returns:
        A Python datetime object.

    Raises:
        ValueError:
            If `date_string` cannot be parsed.
    """
    try:
        # Handle case with microseconds
        dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            # Handle case without microseconds
            dt = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as e:
            raise ValueError(
                f"Cannot parse '{date_string}' as a datetime. Date string is expected to"
                " follow '%Y-%m-%dT%H:%M:%S.%fZ' or '%Y-%m-%dT%H:%M:%SZ' pattern."
            ) from e
    return dt.replace(tzinfo=timezone.utc)  # Set explicit timezone
