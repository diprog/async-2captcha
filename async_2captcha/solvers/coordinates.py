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


from typing import Optional, Union
from pathlib import Path
import base64

class CoordinatesSolver(SolverBase):
    """
    Asynchronous solver for image-based captchas that require clicking specific
    coordinates (e.g., "click the apples" or custom slider captchas).

    This solver uses the 2Captcha 'CoordinatesTask' method, where you provide a
    Base64-encoded image along with optional instructions (comments, min/max clicks, etc.).
    """

    @staticmethod
    def _prepare_captcha_image(captcha_image: Union[str, Path, bytes]) -> str:
        """
        Converts the provided captcha image into a Base64-encoded string,
        which is required for the 'body' field in the 2Captcha API.

        Supported types:
          - bytes: raw image bytes.
          - Path: a pathlib.Path object pointing to an image file.
          - str: either a file path, a Base64-encoded string, or a Data-URI.

        :param captcha_image: The captcha image as a file path, bytes, or Base64/Data-URI string.
        :return: A Base64-encoded string representation of the image.
        :raises ValueError: If the provided captcha_image type is not supported.
        """
        if isinstance(captcha_image, bytes):
            return base64.b64encode(captcha_image).decode('utf-8')
        elif isinstance(captcha_image, Path):
            with captcha_image.open("rb") as f:
                data = f.read()
            return base64.b64encode(data).decode('utf-8')
        elif isinstance(captcha_image, str):
            potential_path = Path(captcha_image)
            if potential_path.exists():
                with potential_path.open("rb") as f:
                    data = f.read()
            else:
                return captcha_image
            if captcha_image.startswith("data:"):
                return captcha_image
            return captcha_image
        else:
            raise ValueError("Unsupported captcha_image type. Provide a str, Path, or bytes.")

    async def create_task(
        self,
        captcha_image: Union[str, Path, bytes],
        comment: Optional[str] = None,
        img_instructions: Optional[str] = None,
        min_clicks: Optional[int] = None,
        max_clicks: Optional[int] = None
    ) -> CoordinatesTask:
        """
        Submits a new CoordinatesTask to 2Captcha and waits for its completion.

        **Usage**:
          - Provide your captcha image as a file path, bytes, or a Base64/Data-URI string.
            If a file path or bytes are provided, they will be automatically converted.
          - Optionally, include a 'comment' or 'img_instructions' to guide the solver.
          - You may also specify 'min_clicks' and 'max_clicks' if the captcha requires a specific number of clicks.

        :param captcha_image: The captcha image as a file path, bytes, or Base64/Data-URI string.
        :param comment: (Optional) A text comment to help workers solve the captcha.
        :param img_instructions: (Optional) An additional instruction image (Base64).
        :param min_clicks: (Optional) The minimum number of clicks required.
        :param max_clicks: (Optional) The maximum number of clicks allowed.
        :return: A CoordinatesTask instance containing status, error info, and solution data.
        :raises TwoCaptchaError: If an error occurs (e.g., invalid key, zero balance, unsolvable captcha).
        """
        # Convert the provided captcha image to the required Base64 format
        body = self._prepare_captcha_image(captcha_image)

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

        task = await self.client.create_task(TaskType.COORDINATES, payload=payload)
        completed_task = await task.wait_until_completed()

        return CoordinatesTask(**completed_task.model_dump())

