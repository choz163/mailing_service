from django.urls import path, reverse_lazy
from .views import ClientList, ClientCreate, ClientUpdate, ClientDelete, HomeView, mailing_send_now, SignUpView, \
    ActivateAccount, MailingAttemptListView, MailingDetailView
from django.contrib.auth import views as auth_views

app_name = 'clients'

urlpatterns = [
    path('', ClientList.as_view(),   name='list'),
    path('add/', ClientCreate.as_view(), name='create'),
    path('<int:pk>/edit/', ClientUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', ClientDelete.as_view(), name='delete'),

    path('', HomeView.as_view(), name='mailing_home'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/<int:pk>/send/', mailing_send_now, name='mailing_send_now'),
    path('attempts/', MailingAttemptListView.as_view(), name='mailingattempt_list'),

    path('', HomeView.as_view(), name='mailing_home'),

    path('signup/', SignUpView.as_view(), name='signup'),
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('password_reset/', auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            success_url=reverse_lazy('password_reset_done')
        ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete')
        ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ), name='password_reset_complete'),


]
