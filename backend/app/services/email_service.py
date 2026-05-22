import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailService:
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = settings.GMAIL_ADDRESS
        self.sender_password = settings.GMAIL_APP_PASSWORD

    def _send(self, msg):
        print(f"EMAIL DEBUG → host={self.smtp_host}")
        print(f"EMAIL DEBUG → sender={self.sender_email}")

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
            server.set_debuglevel(1)

            print("EMAIL DEBUG → opening SMTP")

            server.starttls()

            print("EMAIL DEBUG → logging in")

            server.login(self.sender_email, self.sender_password)

            print("EMAIL DEBUG → sending")

            server.sendmail(
                self.sender_email,
                msg["To"],
                msg.as_string()
            )

            print("EMAIL DEBUG → success")

    def send_status_notification(
        self,
        to_email: str,
        full_name: str,
        application_id: int,
        new_status: str,
        reason: str = None
    ):
        status_display = new_status.replace("_", " ").upper()

        color = (
            "#4CAF50"
            if new_status == "approved"
            else "#f44336"
            if new_status == "rejected"
            else "#FF9800"
        )

        emoji = (
            "✅"
            if new_status == "approved"
            else "❌"
            if new_status == "rejected"
            else "🔍"
        )

        reason_html = (
            f"<p><strong>Reason/Notes:</strong> {reason}</p>"
            if reason
            else ""
        )

        msg = MIMEMultipart("alternative")

        msg["Subject"] = (
            f"{emoji} Loan Application #{application_id} — {status_display}"
        )

        msg["From"] = self.sender_email
        msg["To"] = to_email

        html = f"""
        <html><body>
        <p>Dear <strong>{full_name}</strong>,</p>

        <p>
        Your loan application #{application_id}
        status: {status_display}
        </p>

        {reason_html}

        </body></html>
        """

        msg.attach(MIMEText(html, "html"))

        self._send(msg)

    def send_verification_email(
        self,
        to_email: str,
        full_name: str,
        token: str
    ):
      verify_url = (
    f"https://edi4.onrender.com/api/v1/auth/verify-email?token={token}"
    )

        msg = MIMEMultipart("alternative")

        msg["Subject"] = (
            "Verify your email - AI Credit Scoring"
        )

        msg["From"] = self.sender_email
        msg["To"] = to_email

        html = f"""
        <html><body>

        <h2>Welcome, {full_name}!</h2>

        <p>
        Please verify your email address.
        </p>

        <a href="{verify_url}">
        Verify Email
        </a>

        <p>{verify_url}</p>

        </body></html>
        """

        msg.attach(MIMEText(html, "html"))

        self._send(msg)
