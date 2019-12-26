"""Base classes for transactional emails"""
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail import send_mail
from django.db.utils import ProgrammingError
from html2text import HTML2Text
from render_block.base import render_block_to_string

from .models import SentMail

class Email:
    template = None
    from_email = settings.DEFAULT_FROM_EMAIL

    def __init__(self, ctx, to_email):
        if self.template is None:
            raise ProgrammingError("Email subclasses must set template")

        self.to_email = to_email

        ctx = {'BASE_URL': settings.BASE_URL, **ctx}
        self.ctx = ctx

        self.subject = render_block_to_string(
            self.template, 'subject', ctx).strip()
        self.plain = render_block_to_string(
            self.template, 'plain', ctx).strip()

        # Make links absolute
        soup = BeautifulSoup(render_block_to_string(self.template, 'html', ctx), 'html.parser')
        self._make_links_absolute(soup, settings.BASE_URL)
        self.html = soup.__str__()

        if not self.plain.strip():
            h = HTML2Text()
            h.ignore_images = True
            h.ignore_emphasis = True
            h.ignore_tables = True
            self.plain = h.handle(self.html)

    def send(self):
        send_mail(
            self.subject,
            self.plain,
            self.from_email,
            [self.to_email],
            html_message=self.html
        )

        log = SentMail(
            class_name=self.__class__.__name__,
            email_address=self.to_email,
            subject=self.subject,
            plain_body=self.plain,
            html_body=self.html
        )
        if hasattr(self, 'user'):
            log.user = self.user # pylint: disable=no-member
        log.save()

        self.after_send(log=log) # pylint: disable=no-member

    def after_send(self, *args, **kwargs):
        """Called after an email is sent"""

    @staticmethod
    def _make_links_absolute(soup, base_url):
        """Make all src and href attrs in this document absolute using base_url"""

        if soup.head.base and soup.head.base.get('href'):
            base_url = soup.head.base['href']
        else:
            base_tag = soup.new_tag('base')
            base_tag['href'] = base_url
            soup.head.append(base_tag)

        for att in ('src', 'href'):
            tags = soup.findAll(attrs={att: True})
            for tag in tags:
                tag[att] = urljoin(base_url, tag[att])

class UserEmail(Email):
    def __init__(self, ctx, user):
        self.user = user
        ctx = {'user': user, **ctx}

        super().__init__(ctx, user.email)


class AdminEmail(Email):
    def __init__(self, ctx):
        super().__init__(ctx, None)

    def send(self):
        mail_admins(
            self.subject,
            self.plain,
            html_message=self.html
        )
