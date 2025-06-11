import datetime
from invoices.models import Invoice
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
import os

def generate_invoice_pdf(invoice):
    html = render_to_string("invoices/invoice.html", {'invoice': invoice})
    media_root = settings.MEDIA_ROOT
    invoices_dir = os.path.join(media_root, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    pdf_path = os.path.join(invoices_dir, f"invoice_{invoice.invoice_number or invoice.id}.pdf")

    with open(pdf_path, 'wb') as output:
        pisa_status = pisa.CreatePDF(html, dest=output)
        if pisa_status.err:
            raise Exception("PDF Generation failed")

    invoice.pdf_file = f"invoices/{os.path.basename(pdf_path)}"
    # invoice.save(update_fields=["pdf_file"])

def generate_invoice_number():
    year = datetime.datetime.now().year
    last_invoice = Invoice.objects.filter(invoice_number__endswith=f'-{year}').order_by('invoice_number').last()

    if last_invoice and last_invoice.invoice_number:
        last_number = int(last_invoice.invoice_number.split('-')[0])
    else:
        last_number = 0

    new_number = str(last_number + 1).zfill(4)
    return f"{new_number}-{year}"
