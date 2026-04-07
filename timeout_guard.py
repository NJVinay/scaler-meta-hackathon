"""
timeout_guard.py — Runtime constraint enforcement.

Ensures inference.py stays under the 20-minute limit (vCPU=2, 8GB RAM).
Wraps coroutines with a hard timeout at 19 minutes.
"""

import asyncio
import signal
import sys

MAX_RUNTIME_SECONDS = 1140  # 19 minutes (< 20 min limit, with buffer)


class InferenceTimeoutError(Exception):
    """Raised when inference exceeds the runtime limit."""

    pass


async def run_with_timeout(coro, timeout: int = MAX_RUNTIME_SECONDS):
    """Wrap any coroutine with a hard timeout.

    Args:
        coro:    The coroutine to run.
        timeout: Maximum seconds to allow (default 19 min).

    Returns:
        The coroutine's return value.

    Raises:
        InferenceTimeoutError: If the timeout is exceeded.
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        raise InferenceTimeoutError(
            f"Execution exceeded {timeout}s limit ({timeout // 60} min). "
            f"Terminating to stay under 20-minute constraint."
        )


def setup_sync_timeout(timeout: int = MAX_RUNTIME_SECONDS):
    """Set up a synchronous signal-based timeout (Unix only).

    On Windows, this is a no-op (signal.SIGALRM not available).
    """
    if sys.platform == "win32":
        return  # No SIGALRM on Windows

    def handler(signum, frame):
        raise InferenceTimeoutError(
            f"Execution exceeded {timeout}s limit. Terminating."
        )

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)
