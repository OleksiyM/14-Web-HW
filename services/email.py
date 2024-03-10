"""
Email Services
"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from conf.config import config
from conf import messages
from services.auth import auth_service

conf = ConnectionConfig(MAIL_USERNAME=config.MAIL_USERNAME,
                        MAIL_PASSWORD=config.MAIL_PASSWORD,
                        MAIL_FROM=config.MAIL_USERNAME,
                        MAIL_PORT=config.MAIL_PORT,
                        MAIL_SERVER=config.MAIL_SERVER,
                        MAIL_FROM_NAME="Contacts App",
                        MAIL_STARTTLS=True,
                        MAIL_SSL_TLS=False,
                        USE_CREDENTIALS=True,
                        VALIDATE_CERTS=True,
                        TEMPLATE_FOLDER=Path(__file__).parent / "templates", )


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send email to user
    :param email: Email address
    :param username: Username
    :param host: Host
    :return: None
    """
    # print(f"Sending email to {email}")
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(subject=messages.EMAIL_CONFIRMATION_SUBJECT,
                                recipients=[email],
                                template_body={"host": host, "username": username, "token": token_verification},
                                subtype=MessageType.html)
        fm = FastMail(conf)
        # print(f"{message}")
        await fm.send_message(message, template_name="email_verification.html")
    except ConnectionErrors as err:
        print(f"Error: {err}")
