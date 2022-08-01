from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

@shared_task(bind=True)
def send_email(self,emailto,bid):
    subject = 'Hey! Your bid has been accepted'
    message = f'The bid you sent for' + bid.job.name + 'was approved.\n Contact' + bid.job.uploaded_by + '\n Email : ' + bid.job.uploaded_by.email + '\n Phone number : ' + bid.job.uploaded_by.bio.phone + '\n Have a great day :)'
    email_from = settings.EMAIL_HOST_USER
    recipient = [emailto, ]
    send_mail(subject, message, email_from, recipient)