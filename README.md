# automatic_billing
Reads billing data from an csv file and creates all corresponding bills. As an option, it can also send out all those bills to the specified email adresses. This project is a very simple, small proof of concept which can be improved and tailored to client requirements.
## How will this save your company time?
- Automatic pdf generation with no intermediate steps in word
- No manual data entry
- Support multiple services per client
- Automatic invoice number management
- Fully customizable HTML template ensures a professional appearance for the invoices
- Accurately calculates totals, integrating taxes, different rates for different works,...
- **Scalability**: Works just as well with 10 clients as with 10000
## Features
- Read client and service data from CSV files
- Generate professional PDFs for each client
- Use a customizable HTML template with placeholders
- Save PDF files in an output/ folder
- Send them to the email adresses in the client data file
## Project structure
automatic_bill_creator/
│
├── input/
│ ├── company_data.csv # Basic company data such as name, adress, email,... for the invoice heading (see below for example file)
│ └── clients_services.csv # Client and service data (see below for example file)
├── output/ # Destination folder for the invoices
├── resources/
│ ├── invoice_template.html # HTML template for the invoices
├── main.py # Script principal pour générer les PDF
└── output/ # Dossier de sortie pour les PDF générés

## Technologies used
- **Python 3.8+:** for data processing and automation
- **jinja2:** to render HTML templates dynamically
- **pdfkit & wkhtmltopdf:** to convert HTML templates to PDF files

## How it works
The workflow is very simple (keep in mind, this is a demo with only basic functions):
1) You provide your company info and client/service data in simple CSV files (see below for the example files)
2) Run the script
3) PDFs are automatically sent to clients and stored for your records

## File examples
This demo takes in one **company_data.csv** file of the form
<table>
    <tr>
        <td><strong>company name</strong></td>
        <td>Example LLC</td>
    </tr>
    <tr>
        <td><strong>street adress</strong></td>
        <td>Main street, 1</td>
    </tr>
    <tr>
        <td><strong>zip code</strong></td>
        <td>100001</td>
    </tr>
    <tr>
        <td><strong>city</strong></td>
        <td>New York</td>
    </tr>
    <tr>
        <td><strong>company name</strong></td>
        <td>Example LLC</td>
    </tr>
    <tr>
        <td><strong>phone</strong></td>
        <td>123456789</td>
    </tr>
    <tr>
        <td><strong>email</strong></td>
        <td>company@example.com</td>
    </tr>
    <tr>
        <td><strong>last invoice number</strong></td>
        <td>0</td>
    </tr>


and one **clients_services.csv** file of the form


