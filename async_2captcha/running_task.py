import asyncio
from typing import TYPE_CHECKING

from async_2captcha.http_session import HTTPSession
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


