
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.staticfiles.storage import staticfiles_storage

def send_welcome_email(user_email, user_name, activation_link):
    """
    Sends a welcome email to a user with an activation link.

    Args:
        user_email (str): The user's email address.
        user_name (str): The user's name.
        activation_link (str): The link to activate the user's account.
    """
    context = {
        'user_name': user_name,
        'activation_link': activation_link,
        'STATIC_URL': staticfiles_storage.url(''), 
    }
    html_content = render_to_string('emails/welcome_email.html', context)
    text_content = f"Hello {user_name},\n\nPlease activate your account here: {activation_link}"
    email = EmailMultiAlternatives(
        subject="Activate Your LeaseLoop Account",
        body=text_content, 
        from_email="noreply@lease-loop.com",
        to=[user_email],
    )
    email.attach_alternative(html_content, "text/html") 
    email.send()