from typing import Optional, Dict


class TwoCaptchaError(Exception):
    """
    Base exception for 2captcha-specific errors.

    Stores the numeric error ID, the string error code from 2captcha (if any),
    and a human-readable description (if provided).
    """

    def __init__(
            self,
            error_id: int,
            error_code: Optional[str] = None,
            error_description: Optional[str] = None
    ) -> None:
        self.error_id = error_id
        self.error_code = error_code
        self.error_description = error_description

        # Construct a default message if one is not explicitly provided
        message_parts = []
        if error_code:
            message_parts.append(f"code={error_code}")
        if error_description:
            message_parts.append(f"description={error_description}")

        # Final message for the exception
        message = (
                f"2captcha error [ID={error_id}"
                + ("] " if message_parts else "]")
                + ", ".join(message_parts)
        )
        super().__init__(message)


# --- Individual error classes for known error IDs ---

class ErrorKeyDoesNotExist(TwoCaptchaError):
    """ERROR_KEY_DOES_NOT_EXIST (ID=1): Incorrect or missing API key."""


class ErrorNoSlotAvailable(TwoCaptchaError):
    """ERROR_NO_SLOT_AVAILABLE (ID=2): Bid is too low or queue is too long."""


class ErrorZeroCaptchaFilesize(TwoCaptchaError):
    """ERROR_ZERO_CAPTCHA_FILESIZE (ID=3): Image size is < 100 bytes."""


class ErrorTooBigCaptchaFilesize(TwoCaptchaError):
    """ERROR_TOO_BIG_CAPTCHA_FILESIZE (ID=4): Image size is > 100 kB or exceeds 600px."""


class ErrorPageurl(TwoCaptchaError):
    """ERROR_PAGEURL (ID=5): 'websiteURL' missing or incorrect format."""


class ErrorZeroBalance(TwoCaptchaError):
    """ERROR_ZERO_BALANCE (ID=10): Account has insufficient funds."""


class ErrorIpNotAllowed(TwoCaptchaError):
    """ERROR_IP_NOT_ALLOWED (ID=11): Request is from IP not in trusted IP list."""


class ErrorCaptchaUnsolvable(TwoCaptchaError):
    """ERROR_CAPTCHA_UNSOLVABLE (ID=12): Workers cannot solve the captcha."""


class ErrorBadDuplicates(TwoCaptchaError):
    """ERROR_BAD_DUPLICATES (ID=13): 100% accuracy feature: too many tries, not enough matches."""


class ErrorNoSuchMethod(TwoCaptchaError):
    """ERROR_NO_SUCH_METHOD (ID=14): Request made with an unsupported API method."""


class ErrorImageTypeNotSupported(TwoCaptchaError):
    """ERROR_IMAGE_TYPE_NOT_SUPPORTED (ID=15): Unsupported image format or corrupted image."""


class ErrorNoSuchCapchaId(TwoCaptchaError):
    """ERROR_NO_SUCH_CAPCHA_ID (ID=16): Incorrect captcha ID provided."""


class ErrorIpBlocked(TwoCaptchaError):
    """ERROR_IP_BLOCKED (ID=21): IP is banned due to improper API usage."""


class ErrorTaskAbsent(TwoCaptchaError):
    """ERROR_TASK_ABSENT (ID=22): 'task' property is missing in the request payload."""


class ErrorTaskNotSupported(TwoCaptchaError):
    """ERROR_TASK_NOT_SUPPORTED (ID=23): 'task.type' is unsupported or misspelled."""


class ErrorRecaptchaInvalidSitekey(TwoCaptchaError):
    """ERROR_RECAPTCHA_INVALID_SITEKEY (ID=31): 'sitekey' is invalid."""


class ErrorAccountSuspended(TwoCaptchaError):
    """ERROR_ACCOUNT_SUSPENDED (ID=55): Access blocked for improper API usage."""


class ErrorBadProxy(TwoCaptchaError):
    """ERROR_BAD_PROXY (ID=130): Invalid proxy parameters or unreachable proxy."""


class ErrorBadParameters(TwoCaptchaError):
    """ERROR_BAD_PARAMETERS (ID=110): Missing or incorrectly formatted request parameters."""


class ErrorBadImgInstructions(TwoCaptchaError):
    """ERROR_BAD_IMGINSTRUCTIONS (ID=115): 'imgInstructions' is invalid, corrupted, or too large."""


# --- Mapping from numeric error IDs to their corresponding exceptions ---

ERRORS_MAP: Dict[int, type] = {
    1: ErrorKeyDoesNotExist,
    2: ErrorNoSlotAvailable,
    3: ErrorZeroCaptchaFilesize,
    4: ErrorTooBigCaptchaFilesize,
    5: ErrorPageurl,
    10: ErrorZeroBalance,
    11: ErrorIpNotAllowed,
    12: ErrorCaptchaUnsolvable,
    13: ErrorBadDuplicates,
    14: ErrorNoSuchMethod,
    15: ErrorImageTypeNotSupported,
    16: ErrorNoSuchCapchaId,
    21: ErrorIpBlocked,
    22: ErrorTaskAbsent,
    23: ErrorTaskNotSupported,
    31: ErrorRecaptchaInvalidSitekey,
    55: ErrorAccountSuspended,
    130: ErrorBadProxy,
    110: ErrorBadParameters,
    115: ErrorBadImgInstructions,
}


def raise_for_error_id(
        error_id: int,
        error_code: Optional[str] = None,
        error_description: Optional[str] = None
) -> None:
    """
    Raise an appropriate 2captcha error exception based on the given error ID.

    :param error_id: The numeric error ID from 2captcha response.
    :param error_code: The string error code, e.g. "ERROR_NO_SLOT_AVAILABLE".
    :param error_description: A human-readable description for the error.
    :raises TwoCaptchaError: Subclassed exception if error_id != 0.
    :return: None if error_id == 0 (i.e. no error).
    """
    if error_id == 0:
        return

    exception_cls = ERRORS_MAP.get(error_id, TwoCaptchaError)
    raise exception_cls(error_id, error_code, error_description)
