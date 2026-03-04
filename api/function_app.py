import json
import logging
import os
import azure.functions as func
from azure.communication.email import EmailClient

app = func.FunctionApp()

RECIPIENT_EMAIL = "info@connectedcode.org"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "DoNotReply@connectedcode.org")

FORM_SUBJECTS = {
    "contact": "New Contact Form Submission",
    "school-events": "New School Events Enquiry",
    "teacher-pd": "New Teacher PD Enquiry",
}


def build_email_body(data: dict) -> str:
    """Build a plain-text email body from form data."""
    form_type = data.get("formType", "unknown")
    lines = [
        f"Form: {form_type}",
        f"Name: {data.get('firstName', '')} {data.get('lastName', '')}",
        f"Email: {data.get('email', '')}",
    ]

    if "school" in data and data["school"]:
        lines.append(f"School: {data['school']}")
    if "subject" in data and data["subject"]:
        lines.append(f"Subject: {data['subject']}")

    lines.append(f"\nMessage:\n{data.get('message', '(no message)')}")
    return "\n".join(lines)


def build_html_body(data: dict) -> str:
    """Build an HTML email body from form data."""
    form_type = data.get("formType", "unknown")
    rows = [
        f"<tr><td><strong>Name</strong></td><td>{data.get('firstName', '')} {data.get('lastName', '')}</td></tr>",
        f"<tr><td><strong>Email</strong></td><td><a href='mailto:{data.get('email', '')}'>{data.get('email', '')}</a></td></tr>",
    ]

    if "school" in data and data["school"]:
        rows.append(f"<tr><td><strong>School</strong></td><td>{data['school']}</td></tr>")
    if "subject" in data and data["subject"]:
        rows.append(f"<tr><td><strong>Subject</strong></td><td>{data['subject']}</td></tr>")

    rows_html = "\n".join(rows)
    message = data.get("message", "(no message)").replace("\n", "<br>")

    return f"""
    <h2>New {form_type.replace('-', ' ').title()} Submission</h2>
    <table style="border-collapse:collapse; margin-bottom:16px;">
        {rows_html}
    </table>
    <h3>Message</h3>
    <p>{message}</p>
    """


@app.function_name(name="contact")
@app.route(route="contact", methods=["POST", "OPTIONS"], auth_level=func.AuthLevel.ANONYMOUS)
def contact(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Contact form submission received.")

    # Handle CORS preflight
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=204,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
        )

    cors_headers = {"Access-Control-Allow-Origin": "*"}

    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body",
            status_code=400,
            headers=cors_headers,
        )

    # Validate required fields
    required = ["firstName", "lastName", "email", "message"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        return func.HttpResponse(
            json.dumps({"error": f"Missing required fields: {', '.join(missing)}"}),
            status_code=400,
            mimetype="application/json",
            headers=cors_headers,
        )

    form_type = data.get("formType", "contact")
    subject = FORM_SUBJECTS.get(form_type, "New Form Submission from connectedcode.org")

    # Send email via Azure Communication Services
    try:
        connection_string = os.environ["COMMUNICATION_SERVICES_CONNECTION_STRING"]
        email_client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": SENDER_EMAIL,
            "recipients": {
                "to": [{"address": RECIPIENT_EMAIL}],
            },
            "content": {
                "subject": subject,
                "plainText": build_email_body(data),
                "html": build_html_body(data),
            },
            "replyTo": [{"address": data.get("email", "")}],
        }

        poller = email_client.begin_send(message)
        result = poller.result()
        logging.info(f"Email sent. Message ID: {result.message_id}")

    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to send message. Please try again later."}),
            status_code=500,
            mimetype="application/json",
            headers=cors_headers,
        )

    return func.HttpResponse(
        json.dumps({"status": "ok", "message": "Message sent successfully"}),
        status_code=200,
        mimetype="application/json",
        headers=cors_headers,
    )
