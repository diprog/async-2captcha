from typing import Dict, Any

from .enums import TaskType
from .http_session import HTTPSession
from .models.task import Task
from .running_task import RunningTask
from .solvers.coordinates import CoordinatesSolver
from .solvers.turnstile import TurnstileSolver


class Async2Captcha:
    """
    Provides asynchronous methods to interact with the 2Captcha API,
    along with solver classes for specific captcha types.

    Currently, two solver classes are provided out-of-the-box:
    - ``turnstile``: A :class:`TurnstileSolver` for Cloudflare Turnstile captchas.
    - ``coordinates``: A :class:`CoordinatesSolver` for captchas that require
      clicking coordinates on an image (e.g., 'click the apples' type).

    .. note::
       Other solver classes are yet to be implemented. Contributions from
       the community are welcome!

    The session automatically includes the API key in each request body
    under the ``clientKey`` field.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the 2Captcha client.

        :param api_key: Your 2Captcha API key for authorized requests.
        """
        self.api_key: str = api_key
        self.session: HTTPSession = HTTPSession('https://api.2captcha.com',
                                                default_json={"clientKey": self.api_key})

        #: A solver for Cloudflare Turnstile captchas.
        self.turnstile: TurnstileSolver = TurnstileSolver(self)

        #: A solver for image-based captchas requiring clicks on specific coordinates.
        self.coordinates: CoordinatesSolver = CoordinatesSolver(self)

    async def create_task(self, type: TaskType, payload: Dict[str, Any]) -> RunningTask:
        """
        Create a new 2Captcha task.

        This method posts to the ``/createTask`` endpoint, providing
        the task type and any necessary payload parameters (for example,
        site key, page URL, proxy details, etc.). Returns a ``RunningTask``
        instance that can be used to track and wait for the captcha result.

        :param type: The TaskType indicating the type of captcha.
        :param payload: A dictionary with the necessary fields for the task.
        :return: A RunningTask instance that can be used to poll or wait
                 for the task result.
        """
        payload["type"] = type
        data = await self.session.post("/createTask", json={"task": payload})
        return RunningTask(self, data)

    async def get_task_result(self, task_id: int) -> Task:
        """
        Retrieve the result of a previously created 2Captcha task.

        :param task_id: The unique identifier of the task.
        :return: A :class:`Task` model containing the status, solution, or error info.
        """
        data = await self.session.post("/getTaskResult", json={"taskId": task_id})
        task = Task.model_validate(data)
        return task

    async def get_balance(self) -> float:
        """
        Query the current account balance.

        This method posts to the ``/getTaskResult`` endpoint to retrieve
        the user's balance associated with the API key.

        :return: The balance as a floating-point value.
        """
        data = await self.session.post("/getTaskResult")
        return float(data["balance"])
