# async-2captcha

[![PyPI version](https://badge.fury.io/py/async-2captcha.svg)](https://badge.fury.io/py/async-2captcha)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**async-2captcha** is an **asynchronous Python client** for the [2Captcha API](https://2captcha.com/). It provides helper classes for creating and managing captcha-solving tasks, including specialized solvers for Cloudflare Turnstile and image-based captchas (with selectable coordinates). This library is designed to handle common errors gracefully, raising both HTTP exceptions and 2Captcha-specific exceptions when appropriate.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
  - [Cloudflare Turnstile Captcha](#cloudflare-turnstile-captcha)
  - [Coordinates (Image-Click) Captcha](#coordinates-image-click-captcha)
  - [Retrieving Task Results](#retrieving-task-results)
  - [Checking Account Balance](#checking-account-balance)
- [API Reference](#api-reference)
  - [Async2Captcha Class](#async2captcha-class)
  - [Solvers](#solvers)
    - [TurnstileSolver](#turnstilesolver)
    - [CoordinatesSolver](#coordinatessolver)
    - [Not-Yet-Implemented Solvers](#not-yet-implemented-solvers)
  - [Models](#models)
  - [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Asynchronous**: Built on top of [httpx](https://www.python-httpx.org/) and `async/await`, allowing concurrent operations.
- **Multiple Captcha Types**:
  - Cloudflare Turnstile
  - Coordinate-based image captchas (e.g., “click all apples”)
  - (More solver classes can be added or contributed)
- **Exception Handling**:
  - Raises HTTP errors (`4xx` / `5xx`) if the server’s status code is >= 400.
  - Raises 2Captcha-specific errors (e.g., `ERROR_NO_SLOT_AVAILABLE`, `ERROR_ZERO_BALANCE`, etc.) with clear messages.
- **HTTP/2 Support**:
  - For potentially improved performance, you can enable HTTP/2 by installing `httpx[http2]` and passing `http2=True` when creating the `Async2Captcha` client.
- **Convenient**: Automatically includes your 2Captcha API key in each request and provides high-level methods like `get_balance()`.

---

## Installation

Requires **Python 3.8+**.

```bash
pip install async-2captcha
```

If you want **HTTP/2** support (optional), install:
```bash
pip install httpx[http2]
```

---

## Quick Start

### 1. Get Your 2Captcha API Key

1. Sign up or log in to [2Captcha.com](https://2captcha.com/).
2. Navigate to your [account dashboard](https://2captcha.com/setting) to find your **API key**.

### 2. Instantiate the Client

```python
import asyncio

from async_2captcha.client import Async2Captcha

async def main():
    api_key = "YOUR_2CAPTCHA_API_KEY"
    # Pass http2=True if you installed httpx[http2] and want to enable HTTP/2
    captcha_client = Async2Captcha(api_key, http2=True)

    balance = await captcha_client.get_balance()
    print(f"Your 2Captcha balance is: ${balance:.2f}")

asyncio.run(main())
```

---

## Usage Examples

### Cloudflare Turnstile Captcha

**Turnstile** is Cloudflare’s captcha alternative. To solve a Turnstile captcha:

```python
import asyncio

from async_2captcha.client import Async2Captcha

async def solve_turnstile():
    api_key = "YOUR_2CAPTCHA_API_KEY"
    client = Async2Captcha(api_key)

    # For a normal Turnstile widget (proxyless):
    task_result = await client.turnstile.create_task(
        website_url="https://example.com/login",
        website_key="0x4AAAAAAAA...",
    )
    
    # If the task succeeded, you'll receive a TurnstileTask object with a solution field:
    if task_result.solution:
        print("Turnstile token:", task_result.solution.token)
        print("User agent used:", task_result.solution.user_agent)
    else:
        print("No solution found or an error occurred.")

asyncio.run(solve_turnstile())
```

- **Proxy Support**: To use your own proxy, provide a `proxy_url` such as `"http://user:pass@1.2.3.4:8080"` or `"socks5://..."` to `create_task()`. The solver will automatically switch to a proxy-based task.

### Coordinates (Image-Click) Captcha

Some captchas require clicking specific regions of an image. Use the **CoordinatesSolver**:

```python
import asyncio
import base64

from async_2captcha.client import Async2Captcha

async def solve_coordinates():
    api_key = "YOUR_2CAPTCHA_API_KEY"
    client = Async2Captcha(api_key)

    # Prepare the image as a base64 string
    with open("captcha.jpg", "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    # Create and wait for the coordinates task
    task_result = await client.coordinates.create_task(
        body=image_data, 
        comment="Click all the apples in the image."
    )
    
    # On success, you'll have a list of (x, y) coordinates
    if task_result.solution:
        print("Coordinates:", task_result.solution.coordinates)
    else:
        print("No solution found or an error occurred.")

asyncio.run(solve_coordinates())
```

### Retrieving Task Results

While the included solver classes (`TurnstileSolver`, `CoordinatesSolver`, etc.) automate task creation and waiting, you can also manage tasks directly:

```python
import asyncio
from async_2captcha.client import Async2Captcha
from async_2captcha.enums import TaskType

async def create_and_poll_task():
    api_key = "YOUR_2CAPTCHA_API_KEY"
    client = Async2Captcha(api_key)

    # Create a task manually
    running_task = await client.create_task(TaskType.TURNSTILE_PROXYLESS, payload={
        "websiteURL": "https://example.com",
        "websiteKey": "0x4AAAAAAA..."
    })

    # Poll or wait until completed
    task_result = await running_task.wait_until_completed()
    
    if task_result.is_ready():
        print("Task is solved!", task_result.solution)
    else:
        print("Task is still processing...")

asyncio.run(create_and_poll_task())
```

### Checking Account Balance

```python
import asyncio
from async_2captcha.client import Async2Captcha

async def check_balance():
    client = Async2Captcha("YOUR_2CAPTCHA_API_KEY")
    balance = await client.get_balance()
    print(f"2Captcha balance: ${balance}")

asyncio.run(check_balance())
```

---

## API Reference

### Async2Captcha Class

Located in [`async_2captcha/client.py`](async_2captcha/client.py), the core class:

- **Parameters**:
  - `api_key` (str): 2Captcha API key.
  - `http2` (bool, optional): If `True`, enables HTTP/2 (requires `pip install httpx[http2]`).
- **Attributes**:
  - `turnstile`: A `TurnstileSolver` instance.
  - `coordinates`: A `CoordinatesSolver` instance.
- **Key Methods**:
  1. `create_task(type: TaskType, payload: Dict[str, Any]) -> RunningTask`
     - Creates a captcha task (low-level method).
  2. `get_task_result(task_id: int) -> Task`
     - Fetches result for an existing task.
  3. `get_balance() -> float`
     - Retrieves account balance.

### Solvers

#### TurnstileSolver

- **TurnstileSolver** (`async_2captcha/solvers/turnstile.py`):
  - `create_task(website_url, website_key, action=None, data=None, pagedata=None, proxy_url=None) -> TurnstileTask`
  - Returns a `TurnstileTask` object with the `solution` containing the Turnstile token.

#### CoordinatesSolver

- **CoordinatesSolver** (`async_2captcha/solvers/coordinates.py`):
  - `create_task(body, comment=None, img_instructions=None, min_clicks=None, max_clicks=None) -> CoordinatesTask`
  - Returns a `CoordinatesTask` object, whose `solution` includes a list of clicked coordinates.

#### Not-Yet-Implemented Solvers

The following captcha solvers are currently placeholders (`NotImplementedSolver`). They will raise a `NotImplementedError` if called. Contributions to implement them are welcome.

**Complex captchas:**
- reCAPTCHA V2 (Proxyless and proxy-based): `recaptcha_v2`
- reCAPTCHA V3 (Proxyless and proxy-based): `recaptcha_v3`
- reCAPTCHA V2 Enterprise (Proxyless and proxy-based): `recaptcha_v2_enterprise`
- reCAPTCHA V3 Enterprise: `recaptcha_v3_enterprise`
- Arkose Labs: `arkose_labs`
- GeeTest: `geetest`
- Capy Puzzle: `capy_puzzle`
- Keycaptcha: `keycaptcha`
- Lemin: `lemin`
- Amazon CAPTCHA: `amazon_captcha`
- Cybersiara CAPTCHA: `cybersiara`
- MtCaptcha: `mt_captcha`
- CutCaptcha: `cutcaptcha`
- Friendly CAPTCHA: `friendly_captcha`
- Datadome CAPTCHA: `datadome_captcha`
- ATB CAPTCHA: `atb_captcha`
- Tencent CAPTCHA: `tencent`
- Prosopo CAPTCHA: `prosopo_procaptcha`

**Simple captchas:**
- Normal image-based captchas: `normal_captcha`
- Text-based captchas: `text_captcha`
- Rotational captchas: `rotate`
- Grid-based captchas: `grid`
- Object-drawing captchas: `draw_around`
- Bounding box captchas: `bounding_box`
- Audio captchas: `audio_captcha`

---

### Models

The project uses **Pydantic models** to structure data responses from the 2Captcha API. These models are defined across various files within the `async_2captcha/models/` directory. Notable models include:

- **`Task`** (`models/task.py`):
  - Represents the response from the 2Captcha API for captcha tasks, including status, solution, or error details.
  - Methods:
    - `is_ready()`: Returns `True` if the task is completed and ready.
    - `is_processing()`: Returns `True` if the task is still being processed.

- **`TurnstileTask`** (`solvers/turnstile.py`):
  - Inherits from the `Task` model and includes Turnstile-specific solutions such as tokens and user agents.

- **`CoordinatesTask`** (`solvers/coordinates.py`):
  - Inherits from the `Task` model and includes the list of (x, y) coordinates selected in image-based captchas.

- **Base Models**:
  - **`CamelCaseModel`** (`models/base.py`): A base model used for converting fields between camelCase (used by 2Captcha) and snake_case (used internally).

These models ensure consistency and validation of API responses. When creating new solvers, you can extend these base models to support specific types of captchas.

### Error Handling

**2Captcha always returns HTTP 200** for successful or failed tasks. Errors are indicated by a non-zero `errorId` in the JSON response, at which point a 2Captcha-specific exception is raised. Example codes include:

- `ERROR_NO_SLOT_AVAILABLE` (`errorId=2`)
- `ERROR_ZERO_BALANCE` (`errorId=10`)
- `ERROR_CAPTCHA_UNSOLVABLE` (`errorId=12`)
- … and more.

Additionally, **HTTP errors** (e.g., if 2Captcha.com is unreachable or returns `4xx/5xx`) are raised as `HTTPError` subclasses. Here’s how to handle them:

```python
import asyncio
from async_2captcha.client import Async2Captcha
from async_2captcha.errors.http_errors import HTTPError
from async_2captcha.errors.client_errors import TwoCaptchaError

async def example():
    try:
        client = Async2Captcha("API_KEY", http2=True)
        balance = await client.get_balance()
        print("Balance:", balance)
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except TwoCaptchaError as captcha_err:
        print(f"2Captcha-specific error: {captcha_err}")

asyncio.run(example())
```

---

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request for:

- New captcha solver classes (e.g., reCAPTCHA, GeeTest, etc.).
- Bug fixes, performance improvements, or additional features.
- Documentation enhancements.

### Development Setup

1. **Clone** the repository:
   ```bash
   git clone https://github.com/diprog/async-2captcha.git
   ```
2. **Install** dependencies in a virtual environment:
   ```bash
   cd async-2captcha
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Install** project locally in editable mode:
   ```bash
   pip install -e .
   ```

Please follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines and ensure all tests pass before submitting a pull request.

---

## License

This project is licensed under the [MIT License](LICENSE).  
&copy; 2025 Dmitry. All rights reserved.