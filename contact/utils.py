from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_contact_email(user_email, user_name, message, theme):
    """
    Sends a support ticket email with the given user's name, email, message and theme.

    Args:
        user_email (str): The user's email address.
        user_name (str): The user's name.
        message (str): The user's message.
        theme (str): The theme of the support ticket.
    """
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