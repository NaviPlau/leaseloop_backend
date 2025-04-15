from django.template.loader import render_to_string
from django.conf import settings
import os
from xhtml2pdf import pisa


def generate_invoice_pdf(invoice):
    html = render_to_string("invoices/invoice.html", {'invoice': invoice})
    media_root = settings.MEDIA_ROOT
    invoices_dir = os.path.join(media_root, "invoices")
    os.makedirs(invoices_dir, exist_ok=True) 

    pdf_path = os.path.join(invoices_dir, f"invoice_{invoice.id}.pdf")

    with open(pdf_path, 'wb') as output:
        pisa_status = pisa.CreatePDF(html, dest=output)
        if pisa_status.err:
            raise Exception("PDF Generation failed")

    invoice.pdf_file = f"invoices/invoice_{invoice.id}.pdf"
    invoice.save()
