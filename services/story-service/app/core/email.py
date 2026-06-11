from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_TLS,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fast_mail = FastMail(mail_config)


async def send_verification_email(email: str, token: str) -> None:
    verify_url = f"{settings.FRONTEND_URL}/verify?token={token}"

    message = MessageSchema(
        subject="Подтверждение регистрации — Storytelling",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h2>Добро пожаловать в Storytelling!</h2>
            <p>Для активации аккаунта перейдите по ссылке:</p>
            <a href="{verify_url}"
               style="
                 display:inline-block;
                 padding:12px 24px;
                 background:#4F46E5;
                 color:white;
                 border-radius:6px;
                 text-decoration:none;
               ">
              Подтвердить email
            </a>
            <p style="color:#888; font-size:12px; margin-top:16px;">
              Ссылка действительна 24 часа.<br>
              Если вы не регистрировались — просто проигнорируйте это письмо.
            </p>
        </body>
        </html>
        """,
        subtype=MessageType.html,
    )

    await fast_mail.send_message(message)
