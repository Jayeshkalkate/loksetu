from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_role_groups(sender, **kwargs):
    """Idempotent: (re)create the Officers / Department Admins groups with their permissions."""
    from django.contrib.auth.models import Group, Permission
    view_change = ['view_complaint', 'change_complaint', 'view_evidence', 'view_statushistory']
    # NOTE: audit logs are intentionally NOT included here. AuditLog has no department
    # field, so any group with view_auditlog can see every department's audit trail.
    # Only real Django superusers (role=SUPER) can view audit logs — see audit/admin.py.
    groups = {'Officers': view_change, 'Department Admins': view_change}
    for name, codenames in groups.items():
        g, _ = Group.objects.get_or_create(name=name)
        g.permissions.set(Permission.objects.filter(
            codename__in=codenames, content_type__app_label__in=['complaints', 'audit']))


class Config(AppConfig):
    name = 'accounts'

    def ready(self):
        # Runs after every app's migrate so permissions from complaints/audit exist by the last call.
        post_migrate.connect(create_role_groups, dispatch_uid='loksetu_role_groups')

