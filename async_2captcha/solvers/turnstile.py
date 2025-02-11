from typing import Optional

from pydantic import Field

from .base import SolverBase
from ..enums import TaskType
from ..models.base import CamelCaseModel
from ..models.task import Task
from ..utils import parse_proxy_url


class TurnstileSolution(CamelCaseModel):
    """
    Represents the solution for a Cloudflare Turnstile captcha.

    For a successful captcha solve, the 2Captcha API returns a Turnstile token.
    You typically need to pass this token back to the target page, often in an
    input named "cf-turnstile-response" or "g-recaptcha-response" (for
    compatibility mode).

    In Cloudflare Challenge pages, a userAgent may be required for final
    submission. This model provides both the token and user agent string.
    """

    token: str = Field(
        ...,
        description=(
            "Cloudflare Turnstile token proving the captcha was solved. "
            "Pass this token to the target form, typically under "
            "'cf-turnstile-response' or 'g-recaptcha-response' fields."
        )
    )
    user_agent: str = Field(
        ...,
        description=(
            "User agent used during captcha solving. "
            "Particularly important for Cloudflare Challenge pages."
        )
    )


class TurnstileTask(Task):
    """
    Model for a Turnstile task result.

    Inherits standard task fields (e.g., errorId, status, etc.) from the base
    Task model, and adds a Turnstile-specific solution that includes the token
    and userAgent when the captcha is successfully solved.

    Fields:
      - errorId / errorCode / errorDescription: Represent error status
        if the task failed or captcha was unsolvable.
      - status: 'processing' if the captcha is still being solved,
                'ready' if it is solved.
      - solution: A TurnstileSolution containing the token (and user agent if
                  required).
    """

    solution: Optional[TurnstileSolution] = Field(
        None,
        description="Solution object containing the Turnstile token and user agent."
    )


class TurnstileSolver(SolverBase):
    """
    Asynchronous solver for Cloudflare Turnstile captchas.

    This solver supports two major scenarios:
    1. **Standalone Captcha**: Only `website_url` and `website_key` are needed.
    2. **Cloudflare Challenge Page**: Additional parameters `action`, `data`
       (cData), and `pagedata` (chlPageData) may be required.

    If a `proxy_url` is provided, the solver creates a TurnstileTask (using
    your custom proxy). Otherwise, it creates a TurnstileTaskProxyless (using
    the 2Captcha proxy pool, if needed).
    """

    async def create_task(
            self,
            website_url: str,
            website_key: str,
            action: Optional[str] = None,
            data: Optional[str] = None,
            pagedata: Optional[str] = None,
            proxy_url: Optional[str] = None
    ) -> TurnstileTask:
        """
        Create a new Turnstile captcha task and wait for its completion.

        **Usage**:
        - For a standalone Turnstile captcha, supply only `website_url` and `website_key`.
        - For a Cloudflare Challenge page, also provide `action`, `data` (cData),
          and `pagedata` (chlPageData) from the page's `turnstile.render` call.
        - If a `proxy_url` is given (e.g. "socks5://user:pass@1.2.3.4:1080"),
          a TurnstileTask (proxy-based) is created. If not, a proxyless task is used.

        **Examples**:
        - Standalone Captcha (TurnstileTaskProxyless):
          ```
          solver.create_task(
              website_url="https://example.com",
              website_key="3x00000000000000000000FF"
          )
          ```
        - Cloudflare Challenge page with proxy (TurnstileTask):
          ```
          solver.create_task(
              website_url="https://example.com",
              website_key="3x00000000000000000000FF",
              action="managed",
              data="80001aa1affffc21",
              pagedata="3gAFo2l...55NDFPRFE9",
              proxy_url="http://user:pass@1.2.3.4:8080"
          )
          ```

        :param website_url: URL of the page where the Turnstile widget/challenge is located.
        :param website_key: The Turnstile sitekey (e.g., "3x00000000000000000000FF").
        :param action: (Optional) Action param from `turnstile.render` (for Challenge pages).
        :param data: (Optional) The `cData` from `turnstile.render` (for Challenge pages).
        :param pagedata: (Optional) The `chlPageData` from `turnstile.render` (for Challenge pages).
        :param proxy_url: (Optional) A proxy URL if you want to solve the captcha via your proxy.
                          If provided, the task type will be TurnstileTask; otherwise, TurnstileTaskProxyless.
        :return: A TurnstileTask instance with final status and a TurnstileSolution if solved.
        :raises TwoCaptchaError: If an error occurs (e.g. invalid key, zero balance, unsolvable captcha).
        """
        task_type = TaskType.TURNSTILE if proxy_url else TaskType.TURNSTILE_PROXYLESS

        payload = {
            "websiteURL": website_url,
            "websiteKey": website_key,
        }
        if action:
            payload["action"] = action
        if data:
            payload["data"] = data
        if pagedata:
            payload["pagedata"] = pagedata

        # Parse and attach proxy parameters if a proxy_url is provided
        if proxy_url:
            payload.update(parse_proxy_url(proxy_url))

        # Create the task on 2Captcha and wait for its completion
        task = await self.client.create_task(task_type, payload=payload)
        completed_task = await task.wait_until_completed()

        # Convert the final response into a TurnstileTask model
        return TurnstileTask(**completed_task.model_dump())
