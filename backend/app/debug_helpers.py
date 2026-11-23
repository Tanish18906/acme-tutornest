"""Support debugging helpers (demo: this file adds a new personal data leak on purpose; all values are synthetic)."""
import logging

logger = logging.getLogger("tutornest.debug")


def log_support_lookup(email: str, phone: str, aadhaar: str) -> None:
    # Same mistake as the planted signup log in main.py: personal data goes to the log in plain text.
    logger.info("support lookup email=%s phone=%s aadhaar=%s", email, phone, aadhaar)


def demo_call() -> None:
    log_support_lookup("asha.demo@example.test", "9000000001", "234567890123")
