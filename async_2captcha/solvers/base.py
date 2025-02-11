from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Async2Captcha


class SolverBase:
    """
    Base class for all solver implementations.

    Provides a reference to the Async2Captcha client that can be used
    to create and manage tasks specific to different captcha types.
    """

    def __init__(self, client: "Async2Captcha") -> None:
        """
        Initialize the solver with a reference to the 2Captcha client.

        :param client: An instance of Async2Captcha used for making API calls.
        """
        self.client = client
