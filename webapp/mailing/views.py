from braces.views import StaffuserRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView, View
from accounts.models import VokoUser
from log import log_event
from mailing.helpers import render_mail_template
from mailing.models import MailTemplate
from ordering.core import get_current_order_round


class ChooseTemplateView(StaffuserRequiredMixin, ListView):
    model = MailTemplate
    template_name = "mailing/admin/mailtemplate_list.html"


class PreviewMailView(StaffuserRequiredMixin, TemplateView):
    template_name = "mailing/admin/preview_mail.html"

    def get_context_data(self, **kwargs):
        context = super(PreviewMailView, self).get_context_data(**kwargs)

        users = [VokoUser.objects.get(pk=uid) for uid in self.request.session.get('mailing_user_ids')]
        context['mailing_users'] = users

        template = MailTemplate.objects.get(pk=self.kwargs.get('pk'))
        context['template'] = template

        context['example'] = render_mail_template(template,
                                                  user=self.request.user,
                                                  order_round=get_current_order_round())

        return context


class SendMailView(StaffuserRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        self.users = [VokoUser.objects.get(pk=uid) for uid in self.request.session.get('mailing_user_ids')]
        self.template = MailTemplate.objects.get(pk=self.kwargs.get('pk'))
        self.current_order_round = get_current_order_round()

        # TODO: Clear users from session. Below code doesn't work
        # request.session['mailing_user_ids'] = []
        # del request.session['mailing_user_ids']

        self._send_mails()

        return HttpResponse("Klaar! <a href='/admin'>Klik</a>")

    def _send_mails(self):
        for user in self.users:
            subject, html_message, plain_message = render_mail_template(self.template,
                                                                        user=user,
                                                                        order_round=self.current_order_round)

            send_mail(subject=subject,
                      message=plain_message,
                      from_email="VOKO Utrecht <info@vokoutrecht.nl>",
                      recipient_list=["%s <%s>" % (user.get_full_name(), user.email)],
                      html_message=html_message)

            log_event(operator=self.request.user,
                      user=user,
                      event="Mail verstuurd met onderwerp '%s'" % subject,
                      extra=html_message)

