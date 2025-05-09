from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.management import call_command
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from .models import Client, Mailing, MailingAttempt
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.views.generic import FormView, View, TemplateView
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.core.mail import send_mail
from django.conf import settings


User = get_user_model()


class MailingListView(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm("mailings.view_all_clients"):
            return qs
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("clients:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ["email", "full_name", "comment"]
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm("mailings.change_all_clients"):
            return qs
        return qs.filter(owner=self.request.user)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("clients:list")

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.has_perm("mailings.delete_all_clients"):
            return qs
        return qs.filter(owner=self.request.user)


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        domain = self.request.get_host()
        subject = "Подтвердите регистрацию"
        message = render_to_string(
            "registration/activation_email.html",
            {
                "user": user,
                "domain": domain,
                "uid": uid,
                "token": token,
                "protocol": "https" if self.request.is_secure() else "http",
            },
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        messages.success(
            self.request,
            "На ваш e-mail отправлена ссылка для подтверждения. Проверьте почту.",
        )
        return super().form_valid(form)


class ActivateAccount(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, "Ваш аккаунт активирован. Теперь можно войти.")
            return redirect("login")
        else:
            return render(request, "registration/activation_invalid.html")


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = "mailings/home.html"
    login_url = "login"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        total_mailings = Mailing.objects.count()
        running_mailings = Mailing.objects.filter(status="RUNNING").count()
        paused_mailings = Mailing.objects.filter(status="PAUSED").count()
        finished_mailings = Mailing.objects.filter(status="FINISHED").count()
        total_clients = Client.objects.count()
        unique_clients = Client.objects.values("email").distinct().count()
        recent_mailings = Mailing.objects.order_by("-created_at")[:5]
        ctx.update(
            {
                "total_mailings": total_mailings,
                "running_mailings": running_mailings,
                "paused_mailings": paused_mailings,
                "finished_mailings": finished_mailings,
                "total_clients": total_clients,
                "unique_clients": unique_clients,
                "recent_mailings": recent_mailings,
            }
        )
        return ctx


@login_required
def mailing_send_now(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)
    if mailing.status == "RUNNING":
        messages.warning(request, "Эта рассылка уже запущена.")
    else:
        try:
            call_command("send_mailing", str(mailing.pk))
            messages.success(request, "Отправка запущена. Смотрите отчёты по попыткам.")
        except Exception as e:
            messages.error(request, f"Не удалось запустить: {e}")
    return redirect("mailing_detail", pk=mailing.pk)


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailings/attempt_list.html"
    context_object_name = "attempts"
    paginate_by = 25

    def get_queryset(self):
        return (
            MailingAttempt.objects.filter(mailing__owner=self.request.user)
            .select_related("mailing", "client")
            .order_by("-created_at")
        )


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)
