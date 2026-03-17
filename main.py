import csv
import pdfkit
from jinja2 import Template
import os

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

def fetch_last_invoice_number():
    """Gets the last invoice number from company_data.csv and updates it"""
    rows = []
    output = 0
    with open('input/company_data.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == 'last invoice number':  
                output = int(row[1])
                row[1] = str(output + 1)
            rows.append(row)

    # Réécrire le fichier
    with open('input/company_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    return output

def collect_invoice_data():
    """Collects data from CSV files"""
    data = {}
    company_data = {}

    # Load company info
    with open("input/company_data.csv", newline="", encoding="utf-8") as g:
        reader = csv.reader(g)
        for row in reader:
            key = row[0].strip()
            value = row[1].strip()
            company_data[key] = value

    # Load client invoice entries
    with open("input/template file.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            client = row["Client name"].strip()
            
            # Cleaning data
            hours = float(row["Hours"])
            rate = float(row["Rate"])
            total = float(row["Total"].replace(",", "."))
            taxes = row["Taxes"]
            if taxes:
                taxes = float(taxes.replace("%", ""))
            else:
                taxes = 0

            entry = {
                "date": row["Date"],
                "description": row["Description"],
                "hours": hours,
                "rate": rate,
                "taxes": taxes,
                "total": total
            }

            # Add client and invoice number if new
            if client not in data:
                invoice_number = fetch_last_invoice_number()
                data[client] = [invoice_number, row["Email"]]

            data[client].append(entry)

    return data, company_data


def create_invoices(data, company_data):
    """Generate PDFs using pdfkit"""
    clients = []
    for client_name, value in data.items():
        invoice_number = value[0]
        email = value[1]
        services = value[2:]
        total_invoice = sum(service['total'] for service in services)

        clients.append({
            'name': client_name,
            'email': email,
            'invoice_number': invoice_number,
            'services': services,
            'total_invoice': total_invoice
        })

    # Load HTML template
    with open("resources/invoice_template.html", "r", encoding="utf-8") as f:
        template_html = f.read()

    # Generate PDF per client
    for client in clients:
        html_filled = Template(template_html).render(
            company_name=company_data.get("company name", ""),
            street_address=company_data.get("adress", ""),
            zip_code=company_data.get("zip code", ""),
            city=company_data.get("city", ""),
            phone=company_data.get("phone", ""),
            email=company_data.get("email", ""),
            client_name=client['name'],
            client_email=client['email'],
            invoice_number=client['invoice_number'],
            services=client['services'],
            total_invoice=client['total_invoice']
        )

        pdf_file = os.path.join(output_dir, f"invoice_{client['name'].replace(' ', '_')}.pdf")
        pdfkit.from_string(html_filled, pdf_file)
        print(f"PDF généré pour {client['name']} → {pdf_file}")


if __name__ == "__main__":
    data_dict, company_info = collect_invoice_data()
    create_invoices(data_dict, company_info)