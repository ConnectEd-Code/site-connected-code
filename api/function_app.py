import json
import logging
import os
import re
import time
import azure.functions as func
from azure.communication.email import EmailClient

app = func.FunctionApp()

RECIPIENT_EMAIL = "info@connectedcode.org"
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "DoNotReply@connectedcode.org")

FORM_SUBJECTS = {
    "contact": "New Contact – Contact Page",
    "school-events": "New Contact – School Events Page",
    "teacher-pd": "New Contact – Teacher PD Page",
    "teacher-pd-curriculum": "New Contact – Teacher PD Curriculum Page",
}

# ---------------------------------------------------------------------------
# Rate limiting (in-memory, resets on cold start — sufficient for a contact
# form on a Consumption plan to block rapid-fire spam)
# ---------------------------------------------------------------------------
MAX_REQUESTS_PER_HOUR = 5
RATE_LIMIT_WINDOW_SECONDS = 3600
_rate_limit_store: dict[str, list[float]] = {}


def check_rate_limit(client_ip: str) -> bool:
    """Return True if the request is allowed, False if rate-limited."""
    now = time.time()
    timestamps = _rate_limit_store.get(client_ip, [])
    # Keep only timestamps inside the current window
    timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW_SECONDS]

    if len(timestamps) >= MAX_REQUESTS_PER_HOUR:
        _rate_limit_store[client_ip] = timestamps
        return False

    timestamps.append(now)
    _rate_limit_store[client_ip] = timestamps
    return True


# ---------------------------------------------------------------------------
# Spam / solicitation detection
# ---------------------------------------------------------------------------
# Patterns that indicate someone is SELLING SEO / web-design services to us
SOLICITATION_PATTERNS = [
    # "I/we can help you with your SEO / website design …"
    r"(?:i|we)\s+(?:can|will|would\s+like\s+to)\s+(?:help|assist)\b.*?"
    r"(?:seo|search\s+engine|website|web\s*design|ranking|traffic|online\s+presence)",
    # "our agency/team offers …"
    r"(?:we|our\s+(?:team|agency|company))\s+(?:offer|provide|specialize|deliver)",
    # "improve / boost / increase your SEO …"
    r"(?:improve|boost|increase|grow|enhance|optimize|skyrocket)\s+(?:your\s+)?"
    r"(?:seo|ranking|traffic|visibility|online\s+presence|search\s+(?:engine\s+)?ranking)",
    # "free SEO audit / website review"
    r"free\s+(?:seo|website|web|site)\s+(?:audit|analysis|review|consultation|assessment)",
    # "first page of google"
    r"first\s+page\s+of\s+google",
    r"top\s+of\s+(?:google|search\s+results)",
    # "SEO service / agency / package …"
    r"(?:seo|web\s*(?:site)?\s*design|digital\s+marketing)\s+"
    r"(?:service|agency|package|expert|specialist|company|proposal|strategy|firm|solution)s?",
    # Link-building / backlinks
    r"link[\s-]building",
    r"backlink",
    # "your website's SEO needs improvement …"
    r"your\s+(?:website|site)(?:'s)?\s+(?:seo|ranking|traffic|performance|design)\s+"
    r"(?:needs|could|is\s+(?:not|poor|lacking|missing))",
    # "get / rank on the first page"
    r"(?:get|rank)\s+(?:on\s+)?(?:the\s+)?first\s+page",
]

# Patterns that indicate a LEGITIMATE enquiry (teacher, student, customer)
LEGITIMATE_PATTERNS = [
    r"(?:course|class|learn|teach|student|workshop|training|curriculum|lesson|"
    r"enrol|enroll|purchase|buy|book|hire\s+(?:you|connected\s*code)|"
    r"your\s+(?:service|course|workshop|program|class))",
    r"for\s+(?:my|our)\s+(?:student|class|school|kid)",
]


def is_solicitation(text: str) -> bool:
    """Return True if the text looks like an unsolicited SEO / web-design pitch.

    Returns False for messages that also contain legitimate course / student /
    purchase language so we don't accidentally block teachers or customers.
    """
    lower = text.lower()

    if not any(re.search(p, lower) for p in SOLICITATION_PATTERNS):
        return False

    # If it also looks like a genuine enquiry, let it through
    if any(re.search(p, lower) for p in LEGITIMATE_PATTERNS):
        return False

    return True


def build_email_body(data: dict) -> str:
    """Build a plain-text email body from form data."""
    form_type = data.get("formType", "unknown")
    lines = [
        f"Form: {form_type}",
        f"Name: {data.get('firstName', '')} {data.get('lastName', '')}",
        f"Email: {data.get('email', '')}",
    ]

    if "phone" in data and data["phone"]:
        lines.append(f"Phone: {data['phone']}")
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

    if "phone" in data and data["phone"]:
        rows.append(f"<tr><td><strong>Phone</strong></td><td>{data['phone']}</td></tr>")
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

    # --- Rate limiting ---
    client_ip = req.headers.get(
        "X-Forwarded-For", req.headers.get("REMOTE_ADDR", "unknown")
    )
    # X-Forwarded-For may contain a chain; use the first (client) IP
    client_ip = client_ip.split(",")[0].strip()

    if not check_rate_limit(client_ip):
        logging.warning(f"Rate limit exceeded for {client_ip}")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "rate_limit",
                    "message": "Too many submissions. Please try again later.",
                }
            ),
            status_code=429,
            mimetype="application/json",
            headers=cors_headers,
        )

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

    # --- Spam / solicitation check ---
    combined_text = " ".join(
        str(data.get(f, "")) for f in ("subject", "message", "firstName", "lastName")
    )
    if is_solicitation(combined_text):
        logging.info(f"Blocked solicitation from {data.get('email')}")
        return func.HttpResponse(
            json.dumps(
                {
                    "error": "solicitation",
                    "message": (
                        "Thanks for reaching out! We're not currently looking "
                        "for SEO, web design, or digital marketing services. "
                        "If you think this was a mistake, please email us "
                        "directly at info@connectedcode.org."
                    ),
                }
            ),
            status_code=422,
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
        # result may be a dict or an object depending on SDK version
        msg_id = result.get("id", "") if isinstance(result, dict) else getattr(result, "message_id", "")
        logging.info(f"Email sent. Message ID: {msg_id}")

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
