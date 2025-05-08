from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    help = 'Создаёт группу Managers и даёт ей view_all_* права'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Managers')
        perms = ['add_mailing', 'change_mailing', 'delete_mailing']
        for codename in perms:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Permission {codename} not found'))
        group.save()
        msg = 'создана' if created else 'обновлена'
        self.stdout.write(self.style.SUCCESS(f'Group "Managers" {msg}'))
