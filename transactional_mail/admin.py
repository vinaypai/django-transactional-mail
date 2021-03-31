from bs4 import BeautifulSoup
from django.contrib import admin
from django.core.paginator import Paginator
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.template.loader import render_to_string
from django.http.response import HttpResponse, Http404
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import SentMail
from . import registry
from .registry import _default_registry

@admin.register(SentMail)
class SentMailAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'class_name', 'subject', 'email_address', 'user',)
    list_filter = ('timestamp', 'class_name', 'email_address')
    readonly_fields = ('html_view', )
    exclude = ('html_body', )

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def get_urls(self):
        urls = [
            path(
                '<int:sentmail_id>/html_body/',
                self.admin_site.admin_view(self.get_html_body),
                name="transactional_mail_sentmail_htmlbody"
            )
        ]
        return urls + super().get_urls()

    def html_view(self, obj):
        return format_html(
            '<iframe width="720" height="300" src="{}"></iframe>',
            reverse('admin:transactional_mail_sentmail_htmlbody', kwargs={'sentmail_id': obj.pk})
        )
    html_view.short_description = 'html_body'

    @xframe_options_exempt
    def get_html_body(self, request, sentmail_id):
        obj = SentMail.objects.get(pk=sentmail_id)
        return HttpResponse(obj.html_body)

class RegisteredEmailType(SentMail):
    class Meta:
        proxy = True


class RegisteredEmailPaginator(Paginator):
    @property
    def count(self):
        return len(_default_registry._registry)

@admin.register(RegisteredEmailType)
class RegisteredEmailAdmin(admin.ModelAdmin):
    paginator = RegisteredEmailPaginator

    def changelist_view(self, request, **kwargs):
        response = super().changelist_view(request, **kwargs)
        response.context_data['summary'] = _default_registry._registry.keys()

        return response

    def get_urls(self):
        urls = [
            path('<slug:name>/preview/',
                self.admin_site.admin_view(self.preview),
                name="transactional_mail_preview"
            )
        ] + super().get_urls()
        return urls

    def preview(self, request, name):
        klass = registry.get_handler(name)
        if not klass:
            raise Http404()

        email = klass.get_for_preview(request)

        if request.GET.get('plain'):
            text = "Subject: %s\n\n%s" % (email.subject, email.plain)
            return HttpResponse(text, content_type="text/plain")
        else:
            # Insert an extra table with email metadata
            extra = render_to_string(
                'admin/transactional_mail/preview_table.html',
                {'email': email}
            )
            soup = BeautifulSoup(email.html, 'html.parser')
            if soup.head.title:
                title = soup.head.title
            else:
                title = soup.new_tag('title')
                soup.head.insert(0, title)
            title.string = email.subject

            soup.body.insert(0, BeautifulSoup(extra, 'html.parser'))
            return HttpResponse(soup.encode())
