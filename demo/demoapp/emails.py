from transactional_mail import registry, emails

@registry.register('newsletter_email')
class NewsletterEmail(emails.Email):
    template = 'demoapp/emails/newsletter_email.html'


@registry.register('user_email')
class UserEmail(emails.UserEmail):
    template = 'demoapp/emails/user_email.html'
