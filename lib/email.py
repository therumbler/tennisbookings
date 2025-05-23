import smtplib
from email.message import EmailMessage
import logging


logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10


def send_email(
    subject,
    body,
    to_email,
    from_email,
    smtp_server,
    smtp_port,
    username=None,
    password=None,
) -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}")
    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=TIMEOUT_SECONDS) as server:
            server.set_debuglevel(1)  # Enable verbose debug output
            logger.info("Connected to SMTP server")
            if username and password:
                server.login(username, password)
            logger.info(f"Sending email to {to_email}")
            server.send_message(msg)

    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP server disconnected: {e}")
        return False

    return True
