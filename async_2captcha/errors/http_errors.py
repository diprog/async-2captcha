class HTTPError(Exception):
    """Базовое исключение для всех HTTP-ошибок."""
    def __init__(self, status_code: int, message: str = ""):
        self.status_code = status_code
        self.message = message or f"HTTP Error {status_code}"
        super().__init__(self.message)


class HTTPClientError(HTTPError):
    """Базовое исключение для 4xx HTTP-ошибок."""
    pass


class HTTPServerError(HTTPError):
    """Базовое исключение для 5xx HTTP-ошибок."""
    pass


# --- 4xx Коды ---
class BadRequest(HTTPClientError):
    """400 Bad Request."""
    pass


class Unauthorized(HTTPClientError):
    """401 Unauthorized."""
    pass


class Forbidden(HTTPClientError):
    """403 Forbidden."""
    pass


class NotFound(HTTPClientError):
    """404 Not Found."""
    pass


class MethodNotAllowed(HTTPClientError):
    """405 Method Not Allowed."""
    pass


class Conflict(HTTPClientError):
    """409 Conflict."""
    pass


class Gone(HTTPClientError):
    """410 Gone."""
    pass


class TooManyRequests(HTTPClientError):
    """429 Too Many Requests."""
    pass


# --- 5xx Коды ---
class InternalServerError(HTTPServerError):
    """500 Internal Server Error."""
    pass


class BadGateway(HTTPServerError):
    """502 Bad Gateway."""
    pass


class ServiceUnavailable(HTTPServerError):
    """503 Service Unavailable."""
    pass


class GatewayTimeout(HTTPServerError):
    """504 Gateway Timeout."""
    pass


# Сопоставление кодов ответа и классов исключений
HTTP_EXCEPTIONS_MAP = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    409: Conflict,
    410: Gone,
    429: TooManyRequests,

    500: InternalServerError,
    502: BadGateway,
    503: ServiceUnavailable,
    504: GatewayTimeout
}


def raise_for_status(status_code: int) -> None:
    """
    Если код статуса >= 400, возбудить соответствующее исключение.
    Если код статуса < 400, функция ничего не делает.
    """
    if status_code < 400:
        return

    # Если код статуса известен, выбрасываем соотв. исключение
    if status_code in HTTP_EXCEPTIONS_MAP:
        raise HTTP_EXCEPTIONS_MAP[status_code](status_code)
    # Иначе смотрим, к какому семейству относится код
    elif 400 <= status_code < 500:
        raise HTTPClientError(status_code)
    elif 500 <= status_code < 600:
        raise HTTPServerError(status_code)
    else:
        # Если код не попадает в диапазон 4xx или 5xx
        raise HTTPError(status_code, "Неизвестная HTTP-ошибка")
