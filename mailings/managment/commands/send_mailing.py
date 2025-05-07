import traceback
from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from django.db import transaction
from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Send mailing by ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **opts):
        mailing_id = opts['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Mailing with id={mailing_id} not found')

        # переводим в статус «запущена»
        mailing.status = 'RUNNING'
        mailing.save(update_fields=['status'])
        self.stdout.write(self.style.NOTICE(f'Started mailing {mailing.id}'))

        # отправляем письма
        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=mailing.from_email or 'from@example.com',
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='SUCCESS',
                )
                self.stdout.write(self.style.SUCCESS(f'OK: {client.email}'))
            except Exception as e:
                err = traceback.format_exc()
                MailingAttempt.objects.create(
                    mailing=mailing,
                    client=client,
                    status='FAIL',
                    server_response=err,
                )
                self.stdout.write(self.style.ERROR(f'FAIL: {client.email}'))

        # отмечаем завершение
        mailing.status = 'COMPLETED'
        mailing.save(update_fields=['status'])
        self.stdout.write(self.style.SUCCESS(f'Completed mailing {mailing.id}'))
