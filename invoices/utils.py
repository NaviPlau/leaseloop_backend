from django.template.loader import render_to_string
import os
from django.conf import settings


#for production use, uncomment the following lines and comment the above lines
#from weasyprint import HTML
# def generate_invoice_pdf(invoice):
#     html = render_to_string("invoices/invoice.html", {'invoice': invoice})
#     pdf_path = os.path.join(settings.MEDIA_ROOT, f"invoices/invoice_{invoice.id}.pdf")

#     HTML(string=html).write_pdf(pdf_path)

#     invoice.pdf_file = f"invoices/invoice_{invoice.id}.pdf"
#     invoice.save()


# for development use, keep the following lines as they are
from xhtml2pdf import pisa
from io import BytesIO

def generate_invoice_pdf(html_content):
    result = BytesIO()
    pisa_status = pisa.CreatePDF(src=html_content, dest=result)
    if pisa_status.err:
        raise Exception("PDF Generation failed")
    return result.getvalue()

