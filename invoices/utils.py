import datetime
from invoices.models import Invoice
from django.template.loader import render_to_string
from django.conf import settings
from xhtml2pdf import pisa
import os
from lease_auth.models import UserLogo
import pathlib
from django.contrib.staticfiles import finders

def link_callback(uri, rel):
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = finders.find(uri.replace(settings.STATIC_URL, ""))
    else:
        return uri 

    if not os.path.isfile(path):
        raise Exception(f"Media URI not found: {path}")
    return path

def generate_invoice_pdf(invoice):
    logo_path = None
    try:
        user = invoice.booking.property.owner
        user_logo = UserLogo.objects.filter(user=user).first()
        if user_logo and user_logo.logo and hasattr(user_logo.logo, 'path'):
            logo_path = user_logo.logo.url

    except Exception as e:
        print(f"⚠️ Could not resolve user logo: {e}")

    context = {
        'invoice': invoice,
        'logo_path': logo_path,
    }

    html = render_to_string("invoices/invoice.html", context)
    media_root = settings.MEDIA_ROOT
    invoices_dir = os.path.join(media_root, "invoices")
    os.makedirs(invoices_dir, exist_ok=True)

    pdf_path = os.path.join(invoices_dir, f"invoice_{invoice.invoice_number or invoice.id}.pdf")

    with open(pdf_path, 'wb') as output:
        pisa_status = pisa.CreatePDF(html, dest=output, link_callback=link_callback)
        if pisa_status.err:
            raise Exception("PDF Generation failed")

    invoice.pdf_file = f"invoices/{os.path.basename(pdf_path)}"
    invoice.save(update_fields=["pdf_file"])

def generate_invoice_number():
    year = datetime.datetime.now().year
    last_invoice = Invoice.objects.filter(invoice_number__endswith=f'-{year}').order_by('invoice_number').last()

    if last_invoice and last_invoice.invoice_number:
        last_number = int(last_invoice.invoice_number.split('-')[0])
    else:
        last_number = 0

    new_number = str(last_number + 1).zfill(4)
    return f"{new_number}-{year}"
