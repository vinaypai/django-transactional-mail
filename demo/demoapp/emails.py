from transactional_mail import registry, emails

@registry.register('newsletter_email')
class NewsletterEmail(emails.Email):
    template = 'demoapp/emails/newsletter_email.html'


