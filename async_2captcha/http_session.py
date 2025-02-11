from typing import Optional, Dict, Any

import httpx

from .errors.client_errors import raise_for_error_id
from .errors.http_errors import raise_for_status


class HTTPSession:
    """
    An asynchronous HTTP session tailored for communicating with the 2captcha.com API.

    This class ensures that all POST requests are handled appropriately:
    - If a non-2xx status code is returned, a corresponding HTTP exception is raised.
    - If the 2Captcha API responds with a non-zero 'errorId', a 2Captcha-specific
      exception is raised based on the error code and description.

    .. note::
       The 2captcha API exclusively uses POST requests.

    .. note::
       This class supports HTTP/2 by passing the ``http2=True`` parameter during initialization.
       To use HTTP/2, install the optional dependencies using:

       ```
       pip install httpx[http2]
       ```

    Attributes:
        base_url (Optional[str]): The base URL used to construct POST request URLs.
        default_json (Optional[dict]): Default JSON payload to include in each request.
        http2 (Optional[bool]): If ``True``, enables HTTP/2 for all requests.
    """

    def __init__(self,
                 base_url: Optional[str] = None,
                 default_json: Optional[dict] = None,
                 http2: Optional[bool] = None) -> None:
        """
        Initialize an :class:`HTTPSession`.

        :param base_url:
            A base URL used for constructing the request URL if the path provided
            to :meth:`post` is not absolute. If *None*, the path passed to
            :meth:`post` is used verbatim.

        :param default_json:
            A default JSON payload that will be merged into every POST request.
            If additional JSON is passed to :meth:`post`, the two dictionaries
            are combined with the values in ``default_json`` taking precedence
            in case of key conflicts.

        :param http2:
            If ``True``, enables HTTP/2 for all requests. To use this feature, make sure
            to install the required dependencies via:

            ```
            pip install httpx[http2]
            ```
        """
        self.base_url = base_url
        self.default_json = default_json
        self._client = httpx.AsyncClient(http2=http2)

    async def post(self, url_or_path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send an asynchronous POST request and handle common errors.

        If the session was initialized with a base URL, it is combined
        with ``url_or_path`` unless the latter is a fully qualified URL
        (i.e., includes a scheme like ``https://``).

        If the 2Captcha API returns a non-2xx status code, a corresponding
        HTTP exception is raised. If the JSON response includes an
        ``"errorId"`` that is non-zero, a 2Captcha-specific exception
        is raised.

        :param url_or_path:
            The URL or path to send the POST request to. This value is appended
            to ``base_url`` if provided and not already fully qualified.

        :param json:
            A dictionary to be serialized as JSON in the request body. If
            :attr:`default_json` was set, its keys overwrite any conflicts
            here.

        :return:
            The parsed JSON response from the server as a dictionary.

        :raises HTTPError:
            If the server responds with an HTTP error status code (>= 400).

        :raises TwoCaptchaError:
            If the JSON response contains a non-zero ``errorId``, indicating
            a 2Captcha-specific error (e.g. invalid API key, insufficient
            balance, or unsolvable captcha).
        """
        # Construct the full URL if needed
        if not self.base_url:
            url = url_or_path
        else:
            url = url_or_path if "://" in url_or_path else self.base_url + url_or_path

        # Merge default JSON with the provided JSON if applicable
        if self.default_json:
            if json:
                json.update(self.default_json)
            else:
                json = self.default_json

        r = await self._client.post(url, json=json)

        # Raise an HTTP error if the status code indicates failure
        raise_for_status(r.status_code)

        # Parse the JSON response
        data = r.json()

        # Raise a 2Captcha client error based on errorId, if present
        if data.get("errorId"):
            raise_for_error_id(data["errorId"], data.get("errorCode"), data.get("errorDescription"))

        return data
