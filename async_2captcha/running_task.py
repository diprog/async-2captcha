import asyncio
from typing import TYPE_CHECKING

from async_2captcha.models.task import Task

if TYPE_CHECKING:
    from .client import Async2Captcha


class RunningTask:
    def __init__(self, client: "Async2Captcha", task_data: dict):
        self.client = client
        self.task = Task.model_validate(task_data)

    async def wait_until_completed(self) -> Task:
        while True:
            task = await self.client.get_task_result(self.task.task_id)
            if task.is_ready():
                return task
            elif task.is_processing():
                pass
            await asyncio.sleep(10)

    async def report_incorrect(self) -> None:
        """
        Report to the API that the captcha task result is incorrect.

        :raises TwoCaptchaError: If the API request fails.
        """
        await self.client.report_incorrect(self.task.task_id)

    async def report_correct(self) -> None:
        """
        Report to the API that the captcha task result is correct.

        :raises TwoCaptchaError: If the API request fails.
        """
        await self.client.report_correct(self.task.task_id)