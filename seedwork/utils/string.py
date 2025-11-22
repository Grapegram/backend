import re


def camel_to_snake(name: str) -> str:
    """Convert camelCase or PascalCase string to snake_case.

    Examples:
        camel_to_snake('userName') -> 'user_name'
        camel_to_snake('UserName') -> 'user_name'
        camel_to_snake('HTTPResponse') -> 'h_t_t_p_response'
        camel_to_snake('getHTTPResponseCode') -> 'get_h_t_t_p_response_code'
    """
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
