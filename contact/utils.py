from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_contact_email(user_email, user_name, message, theme):
    context = {
        'user_name': user_name,
        'message': message,
        'theme': theme,
        'user_email': user_email
    }
    html_content = render_to_string('emails/contact_email.html', context)
    text_content = f"Theme: {theme}\n\nMessage: {message}"
    email = EmailMultiAlternatives(
        subject="Support Ticket",
        body=text_content, 
        from_email= 'noreply@lease-loop.com',
        to=['noreply@lease-loop.com'],
    )
    email.attach_alternative(html_content, "text/html") 
    email.send()