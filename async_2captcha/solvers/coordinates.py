from typing import Optional, List, Dict

from pydantic import Field

from .base import SolverBase
from ..enums import TaskType
from ..models.base import CamelCaseModel
from ..models.task import Task


class CoordinatesSolution(CamelCaseModel):
    """
    Represents the solution for a CoordinatesTask.

    When the captcha is successfully solved, 2Captcha returns a list of
    (x, y) coordinates that the worker clicked or selected in the image.
    """

    coordinates: List[Dict[str, int]] = Field(
        ...,
        description=(
            "A list of coordinate objects. Each object contains 'x' and 'y' "
            "keys representing the clicked point on the image."
        )
    )


class CoordinatesTask(Task):
    """
    Model for a CoordinatesTask result.

    Inherits standard fields (e.g. errorId, status, etc.) from the base Task model,
    and adds a CoordinatesSolution if the task is successfully solved.

    Fields:
      - errorId / errorCode / errorDescription: Indicate errors if the task failed.
      - status: 'processing' while being solved, 'ready' once solved.
      - solution: A CoordinatesSolution with the worker-chosen click coordinates.
    """

    solution: Optional[CoordinatesSolution] = Field(
        None,
        description="Solution object with a list of (x, y) coordinates."
    )


class CoordinatesSolver(SolverBase):
    """
    Asynchronous solver for image-based captchas that require clicking specific
    coordinates (e.g., 'click the apples' or custom slider captchas).

    This solver uses the 2Captcha 'CoordinatesTask' method, where you provide
    a base64-encoded image and optional instructions (comments, min/max clicks, etc.).
    """

    async def create_task(
        self,
        body: str,
        comment: Optional[str] = None,
        img_instructions: Optional[str] = None,
        min_clicks: Optional[int] = None,
        max_clicks: Optional[int] = None
    ) -> CoordinatesTask:
        """
        Create a new CoordinatesTask and wait for its completion.

        **Usage**:
        - Convert your image to Base64 or Data-URI format.
        - Supply it as the 'body' parameter.
        - Optionally provide a 'comment' or 'img_instructions' to guide the solver.
        - You can also specify 'min_clicks' and 'max_clicks' if the captcha
          requires a specific number of clicks.

        :param body: Base64-encoded image or Data-URI string.
        :param comment: (Optional) A text comment to help workers solve the captcha.
        :param img_instructions: (Optional) An additional instruction image (Base64).
        :param min_clicks: (Optional) The minimum number of clicks required.
        :param max_clicks: (Optional) The maximum number of clicks allowed.
        :return: A CoordinatesTask instance containing status, error info, and solution data.
        :raises TwoCaptchaError: If an error occurs (e.g., invalid key, zero balance, unsolvable).
        """
        # Prepare payload for 2Captcha /createTask
        payload = {
            "body": body,
        }
        if comment:
            payload["comment"] = comment
        if img_instructions:
            payload["imgInstructions"] = img_instructions
        if min_clicks is not None:
            payload["minClicks"] = min_clicks
        if max_clicks is not None:
            payload["maxClicks"] = max_clicks

        # Create the CoordinatesTask on 2Captcha (no proxy support specified by docs).
        task = await self.client.create_task(TaskType.COORDINATES, payload=payload)
        completed_task = await task.wait_until_completed()

        # Convert the final response into a CoordinatesTask model
        return CoordinatesTask(**completed_task.model_dump())
