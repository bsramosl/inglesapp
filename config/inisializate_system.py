import os
from collections import OrderedDict

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import Group, User
from app.models import (
    Person, ProfileUser, SystemRol, ProfileSystemRol,
    AccessGroup, ModuleCategory, Module, ModulePermission, AccessGroupModule
)

def create_user_with_role(username, full_name, email, rol_key, is_superuser=False, is_staff=False):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_superuser': is_superuser,
            'is_staff': is_staff
        }
    )
    if created:
        user.set_password('demo1234')
        user.save()
        print(f"✅ Usuario creado: {username}/demo1234")
    else:
        print(f"ℹ️ El usuario {username} ya existe.")

    person, _ = Person.objects.get_or_create(user=user, defaults={
        'names': full_name.split()[0],
        'surname1': full_name.split()[1] if len(full_name.split()) > 1 else '',
        'surname2': '',
        'email': email
    })

    profile_user, _ = ProfileUser.objects.get_or_create(person=person)

    rol = SystemRol.objects.get(name_key=rol_key)
    ProfileSystemRol.objects.get_or_create(
        profile=profile_user,
        system_rol=rol,
        defaults={'is_active': True, 'is_main': True}
    )

    return profile_user


def run():
    # Crear roles del sistema
    roles = [
        ('Administrador del Sistema', 'admin_system'),
        ('Sistemas', 'system_manager'),
        ('Estudiante', 'student'),
        ('Docente', 'teacher'),
        ('Revisor de contenido', 'content_reviewer'),
    ]
    for name, key in roles:
        SystemRol.objects.get_or_create(
            name=name,
            name_key=key,
            defaults={'description': f'Rol: {name}', 'is_active': True}
        )

    # Crear grupo de acceso solo para administradores
    django_group, _ = Group.objects.get_or_create(name='Administradores del Sistema')
    access_group, _ = AccessGroup.objects.get_or_create(group=django_group, defaults={
        'description': 'Grupo con acceso total al sistema',
        'is_super_admin': True
    })

    categorias_con_modulos = OrderedDict({
        'Administración': [
            ('module_category', 'Categorías'),
            ('access_group', 'Grupos de Acceso'),
            ('module', 'Módulos'),
            ('system_rol', 'Roles del Sistema'),
            ('user_profile', 'Perfiles de Usuario'),
            ('group_module', 'Grupos de Modulos'),
        ],
        'Language': [
            ('language', 'Language'),
            ('language_level', 'Langauge Levels'),
        ],
        'Configuración': [
            ('group_module', 'Grupos de Módulos'),
        ],
    })

    for cat_order, (categoria_nombre, modulos) in enumerate(categorias_con_modulos.items(), start=1):
        category, _ = ModuleCategory.objects.get_or_create(
            name=categoria_nombre,
            defaults={'order': cat_order}
        )

        for mod_order, (code, label) in enumerate(modulos, start=1):
            module, _ = Module.objects.get_or_create(
                category=category,
                name=label,
                defaults={
                    'description': f'Módulo para {label.lower()}',
                    'url': f'/{code}/',
                    'icon': 'settings',
                    'order': mod_order,
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

            # Crear acceso al grupo
            agm, _ = AccessGroupModule.objects.get_or_create(
                access_group=access_group,  # asegúrate de que access_group esté definido antes
                module=module,
                defaults={
                    'can_view': True,
                    'can_edit': True,
                    'can_delete': True,
                    'can_manage': True
                }
            )

            # Asociar permisos del módulo al grupo
            agm.permissions.set(module.permissions.all())

    # Crear usuarios de prueba
    admin_profile = create_user_with_role('admin', 'Admin Root', 'admin@example.com', 'admin_system', True, True)
    admin_profile.access_groups.add(access_group)  # Solo el admin

    create_user_with_role('sistemas', 'Juan Sistemas', 'sistemas@example.com', 'system_manager')
    create_user_with_role('docente', 'Ana Docente', 'docente@example.com', 'teacher')
    create_user_with_role('estudiante', 'Pedro Estudiante', 'estudiante@example.com', 'student')
    create_user_with_role('revisor', 'Laura Revisor', 'revisor@example.com', 'content_reviewer')

    print("✅ Inicialización completa con roles y usuarios de prueba.")

run()
