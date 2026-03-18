import csv
import os
import smtplib
from email.message import EmailMessage

import pdfkit
from dotenv import load_dotenv
from jinja2 import Template

# Load environment variables
load_dotenv()

SENDER_EMAIL = os.getenv("sender_email")
SENDER_PASSWORD = os.getenv("sender_password")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_last_invoice_number() -> int:
    """
    Retrieve the last invoice number from company_data.csv
    and increment it for future use.

    Returns:
        int: The current invoice number before incrementing.
    """
    rows = []
    last_invoice_number = 0

    with open("input/company_data.csv", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == "last invoice number":
                last_invoice_number = int(row[1])
                row[1] = str(last_invoice_number + 1)
            rows.append(row)

    # Rewrite the updated file
    with open("input/company_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    return last_invoice_number


def collect_invoice_data():
    """
    Load and structure invoice data from CSV files.

    Returns:
        tuple:
            - dict: Client data with invoice details
            - dict: Company information
    """
    client_data = {}
    company_data = {}

    # Load company information
    with open("input/company_data.csv", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            key = row[0].strip()
            value = row[1].strip()
            company_data[key] = value

    # Load client services
    with open("input/clients_services.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            client_name = row["Client name"].strip()

            # Clean and convert values
            hours = float(row["Hours"])
            rate = float(row["Rate"])
            total = float(row["Total"].replace(",", "."))

            taxes = row["Taxes"]
            taxes = float(taxes.replace("%", "")) if taxes else 0.0

            service_entry = {
                "date": row["Date"],
                "description": row["Description"],
                "hours": hours,
                "rate": rate,
                "taxes": taxes,
                "total": total,
            }

            # Initialize client entry if not already present
            if client_name not in client_data:
                invoice_number = fetch_last_invoice_number()
                client_data[client_name] = [invoice_number, row["Email"]]

            client_data[client_name].append(service_entry)

    return client_data, company_data


def create_invoices(data, company_data, send_invoices: bool = True):
    """
    Generate PDF invoices and optionally send them via email.

    Args:
        data (dict): Client invoice data
        company_data (dict): Company information
        send_invoices (bool): Whether to send emails after generating PDFs
    """
    clients = []

    # Prepare structured client data
    for client_name, values in data.items():
        invoice_number = values[0]
        email = values[1]
        services = values[2:]

        total_invoice = sum(service["total"] for service in services)

        clients.append(
            {
                "name": client_name,
                "email": email,
                "invoice_number": invoice_number,
                "services": services,
                "total_invoice": total_invoice,
            }
        )

    # Load HTML template
    with open("resources/invoice_template.html", "r", encoding="utf-8") as file:
        template_html = file.read()

    # Generate invoices
    for client in clients:
        html_filled = Template(template_html).render(
            company_name=company_data.get("company name", ""),
            street_address=company_data.get("adress", ""),
            zip_code=company_data.get("zip code", ""),
            city=company_data.get("city", ""),
            phone=company_data.get("phone", ""),
            email=company_data.get("email", ""),
            client_name=client["name"],
            client_email=client["email"],
            invoice_number=client["invoice_number"],
            services=client["services"],
            total_invoice=client["total_invoice"],
        )

        pdf_path = os.path.join(
            OUTPUT_DIR, f"invoice_{client['name'].replace(' ', '_')}.pdf"
        )

        pdfkit.from_string(html_filled, pdf_path)

        if send_invoices:
            send_invoice_email(client["email"], pdf_path)


def send_invoice_email(to_email: str, pdf_path: str):
    """
    Send an invoice PDF via email.

    Args:
        to_email (str): Recipient email address
        pdf_path (str): Path to the PDF file
    """
    msg = EmailMessage()
    msg["Subject"] = "Your Invoice"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    msg.set_content(
        "Hello,\n\nPlease find your invoice attached.\n\nBest regards"
    )

    # Attach PDF
    with open(pdf_path, "rb") as file:
        msg.add_attachment(
            file.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path),
        )

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)


if __name__ == "__main__":
    client_data, company_info = collect_invoice_data()
    create_invoices(client_data, company_info, send_invoices=True)