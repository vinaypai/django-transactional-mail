"""Base classes for transactional emails"""
import re
from urllib.parse import urljoin

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail import send_mail
from django.db.utils import ProgrammingError
from html2text import HTML2Text
from render_block import BlockNotFound, render_block_to_string
from xml.etree import ElementTree

from .models import SentMail

class Email:
    template = None
    from_email = settings.DEFAULT_FROM_EMAIL
    user = None

    def __init__(self, to_email, extra_ctx={}):
        if self.template is None:
            raise ProgrammingError("Email subclasses must set template")

        self.to_email = to_email

        ctx = {
            'BASE_URL': settings.BASE_URL, **extra_ctx
        }

        self.ctx = ctx

    @property
    def subject(self):
        # Templates can end up with unwanted newlines. Convert them all to spaces
        subject: str = render_block_to_string(self.template, 'subject', self.ctx).strip()
        subject = re.sub(r'\s+', ' ', subject)
        return subject

    @property
    def html(self):
        # Make links absolute
        html = render_block_to_string(self.template, 'html', self.ctx)
        root = ElementTree.fromstring(html)

        for att in ('src', 'href'):
            for tag in root.findall(f'.//*[@{att}]'):
                tag.attrib[att] = urljoin(settings.BASE_URL, tag.attrib[att])

        html = ElementTree.tostring(root, method="html", encoding="unicode")
        return html

    @property
    def plain(self) -> str:
        try:
            return render_block_to_string(self.template, 'plain', self.ctx).strip()
        except BlockNotFound:
            h = HTML2Text()
            h.ignore_images = True
            h.ignore_emphasis = True
            h.ignore_tables = True
            return h.handle(self.html)

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
        if self.user:
            log.user = self.user
        log.save()

        self.after_send(log=log) # pylint: disable=no-member

    def after_send(self, *args, **kwargs):
        """Called after an email is sent"""

    @classmethod
    def get_for_preview(cls, request):
        return cls('nobody@example.com')


class UserEmail(Email):
    def __init__(self, user, extra_ctx={}):
        self.user = user
        ctx = {'user': user, **extra_ctx}
        super().__init__(user.email, ctx)

    @classmethod
    def get_for_preview(cls, request):
        if user_id := request.GET.get('user_id', None):
            user = get_user_model().objects.get(pk=user_id)
        else:
            user = request.user

        return cls(user)

class AdminEmail(Email):
    def __init__(self, ctx):
        super().__init__(ctx, None)

    def send(self):
        mail_admins(
            self.subject,
            self.plain,
            html_message=self.html
        )
