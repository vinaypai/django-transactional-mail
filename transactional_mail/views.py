from bs4 import BeautifulSoup
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponse, Http404
from django.template.loader import render_to_string

from . import registry

@staff_member_required
def preview_email(request, email_name):
    klass = registry.get_handler(email_name)
    if not klass:
        raise Http404()

    email = klass.get_for_preview(request)

    if request.GET.get('plain'):
        text = "Subject: %s\n\n%s" % (email.subject, email.plain)
        return HttpResponse(text, content_type="text/plain")
    else:
        # Insert an extra table with email metadata
        extra = render_to_string(
            'transactional_email/preview_table.html',
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
