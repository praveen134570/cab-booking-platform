from celery import Celery
from app.config import settings

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery.task(name="generate_and_send_receipt")
def generate_and_send_receipt(ride_id: int, amount: float, user_email: str):
    html_content = f"""
    <html>
        <head><style>body {{ font-family: Arial, sans-serif; padding: 24px; }}</style></head>
        <body>
            <h1>Ride Receipt</h1>
            <p><strong>Ride ID:</strong> #{ride_id}</p>
            <p><strong>Total Paid:</strong> ${amount:.2f}</p>
            <p><strong>Status:</strong> Completed & Paid</p>
            <p>Thank you for riding with us!</p>
        </body>
    </html>
    """
    try:
        from weasyprint import HTML
        output_path = f"/tmp/receipt_{ride_id}.pdf"
        HTML(string=html_content).write_pdf(output_path)
        return f"PDF Receipt generated at {output_path} for {user_email}"
    except (ImportError, OSError):
        # Fallback for Windows environments without GTK3 libraries
        output_path = f"receipt_{ride_id}.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return f"HTML Receipt saved to {output_path} for {user_email}"  