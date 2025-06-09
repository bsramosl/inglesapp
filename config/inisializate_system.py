import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import Group, User
from app.models import (
    Person, ProfileUser, SystemRol, ProfileSystemRol,
    AccessGroup, ModuleCategory, Module, ModulePermission, AccessGroupModule
)

def run():
    # Crear superusuario si no existe
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={'email': 'admin@example.com', 'is_superuser': True, 'is_staff': True}
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Superusuario creado: admin/admin123")
    else:
        print("ℹ️ El usuario admin ya existe.")

    # Crear persona asociada
    person, _ = Person.objects.get_or_create(user=admin_user, defaults={
        'names': 'Adminis',
        'surname1': 'System',
        'surname2': 'Root',
        'email': 'admin@example.com'
    })

    # Crear perfil de usuario
    profile_user, _ = ProfileUser.objects.get_or_create(person=person)

    # Crear rol principal
    sys_rol, _ = SystemRol.objects.get_or_create(
        name='Administrador del Sistema',
        name_key='admin_system',
        defaults={'description': 'Rol con acceso completo', 'is_active': True}
    )

    # Asignar rol principal
    ProfileSystemRol.objects.get_or_create(
        profile=profile_user,
        system_rol=sys_rol,
        defaults={'is_active': True, 'is_main': True}
    )

    # Crear grupo Django y grupo de acceso con todos los permisos
    django_group, _ = Group.objects.get_or_create(name='Administradores del Sistema')
    access_group, _ = AccessGroup.objects.get_or_create(group=django_group, defaults={
        'description': 'Grupo con acceso total al sistema',
        'is_super_admin': True
    })

    # Asociar grupo de acceso al perfil de usuario (no a la persona)
    profile_user.access_groups.add(access_group)

    # Crear categoría de módulo
    category, _ = ModuleCategory.objects.get_or_create(name='Administración', defaults={'order': 1})

    # Crear módulos y permisos
    modulos = [
        ('module', 'Modules'),
        ('system_rol', 'System Rol'),
        ('profiles', 'Profiles'),
    ]

    for idx, (code, label) in enumerate(modulos, start=1):
        module, _ = Module.objects.get_or_create(
            category=category,
            name=label,
            defaults={
                'description': f'Módulo para {label.lower()}',
                'url': f'/{code}/',
                'icon': 'settings',
                'order': idx,
                'is_active': True,
                'needs_permission': True
            }
        )

        # Crear permisos del módulo
        for codename, name in [
            ('view', f'Puede ver {label}'),
            ('edit', f'Puede editar {label}'),
            ('delete', f'Puede eliminar {label}')
        ]:
            ModulePermission.objects.get_or_create(
                module=module,
                code_name=codename,
                defaults={'name': name, 'description': name}
            )

        # Asignar módulo y permisos al grupo de acceso
        agm, _ = AccessGroupModule.objects.get_or_create(
            access_group=access_group,
            module=module,
            defaults={
                'can_view': True,
                'can_edit': True,
                'can_delete': True,
                'can_manage': True
            }
        )
        agm.permissions.set(module.permissions.all())

    print("✅ Inicialización del sistema completada.")

run()
