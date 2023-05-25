from email.message import EmailMessage
from urllib.parse import quote_plus

import aiosmtplib
from app.env import SETTINGS


async def send_email(to: str, subject: str, content: str) -> None:
    if not SETTINGS.smtp:
        return

    message = EmailMessage()
    message["From"] = SETTINGS.smtp.email
    message["To"] = to
    message["Subject"] = subject
    message.set_charset("utf-8")
    message.set_content(content)

    try:
        await aiosmtplib.send(
            message,
            hostname=SETTINGS.smtp.host,
            port=SETTINGS.smtp.port,
            username=SETTINGS.smtp.username,
            password=SETTINGS.smtp.password,
            timeout=120,
        )
    except TimeoutError:
        pass


async def send_email_verify(to: str, email_secret: str) -> None:
    """Send email verification email.

    Args:
        to (str)
        email_secret (str)
    """

    await send_email(
        to=to,
        subject=f"{SETTINGS.site_name} requires email verification.",
        content=f"Please verify your email for {SETTINGS.site_name} by following the link below.\n\n{SETTINGS.proxy_urls.backend}/controllers/account/{quote_plus(to)}/email/verify/{email_secret}\n\nIf you didn't create this account, please ignore this email.",
    )
