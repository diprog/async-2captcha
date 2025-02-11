from typing import Optional, Dict, Any

from pydantic import Field

from .base import CamelCaseModel


class Task(CamelCaseModel):
    """
    Pydantic model representing a 2captcha task response.

    This model covers all possible fields returned by the getTaskResult method,
    including error details (when the task cannot be completed),
    and task data (when the task is still processing or completed).
    """

    task_id: Optional[int] = Field(
        default=None,
        description="The task ID associated with this result."
    )
    error_id: int = Field(
        description="The error ID (0 if there's no error, otherwise a nonzero code)."
    )
    status: Optional[str] = Field(
        default=None,
        description="Indicates whether the task is 'processing' or 'ready'."
    )
    error_code: Optional[str] = Field(
        default=None,
        description="String code describing the error if the task could not be completed."
    )
    error_description: Optional[str] = Field(
        default=None,
        description="Detailed description of the error if the task could not be completed."
    )
    solution: Optional[Dict[str, Any]] = Field(
        default=None,
        description="An object containing the solution data once the task is completed."
    )
    cost: Optional[str] = Field(
        default=None,
        description="A string indicating the cost of solving the task (e.g. '0.00299')."
    )
    ip: Optional[str] = Field(
        default=None,
        description="The IP address from which the task was submitted."
    )
    create_time: Optional[int] = Field(
        default=None,
        description="Unix timestamp for when the task was created."
    )
    end_time: Optional[int] = Field(
        default=None,
        description="Unix timestamp for when the task was completed."
    )
    solve_count: Optional[int] = Field(
        default=None,
        description="Number of attempts or workers that tried to solve the task."
    )

    def is_ready(self) -> bool:
        """
        Indicates whether the task has completed successfully.

        :return: True if status is "ready", otherwise False.
        """
        return self.status == "ready"

    def is_processing(self) -> bool:
        """
        Indicates whether the task is still being processed.

        :return: True if status is "processing", otherwise False.
        """
        return self.status == "processing"
