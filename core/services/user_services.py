from apps.users.models import People
from core.models import Module


class UserService:
    @staticmethod
    def get_user_profile(user):
        try:
            people = People.objects.get(user=user)
            accessible_modules = Module.objects.filter(accessgroupmodule__access_group__in=people.access_groups.all(),
                                                       accessgroupmodule__can_view=True,is_active=True,visible=True).distinct().select_related('category')
            menu_structure = {}
            for module in accessible_modules:
                if module.category.name not in menu_structure:
                    menu_structure[module.category.name] = {
                        'icon': module.category.icon,
                        'order':module.category.order,
                        'modules':[]
                    }
                    menu_structure[module.category.name]['modules'].append({
                        'name':module.name,
                        'icon':module.icon,
                        'order':module.order,
                        'url':module.url,
                        'permissions': [
                            perm.id for perm in module.permissions.all()
                        ]
                    })

            sorted_categories = sorted(
                menu_structure.items(),
                key=lambda x: x[1]['order']
            )

            ordered_menu = {
                category: {
                    'icon': data['icon'],
                    'modules': sorted(
                        data['modules'],
                        key=lambda x: x['order']
                    )
                }
                for category, data in sorted_categories
            }
            return {
                'id': people.id,
                'username': people.user.username,
                'email': people.email,
                'people': people,
                'last_login': people.user.last_login,
                'date_joined': people.user.date_joined,
                'menu': ordered_menu,
                'permissions': list(people.get_user_permissions()),
                # Agrega más campos según tu modelo de usuario
            }
        except Exception as e:
            print (e)

def actualizar_datos_sesion(request, user=None):

    if user is None:
        user = request.user

    if user.is_authenticated:
        user_profile = UserService.get_user_profile(user)
        request.session['user_profile'] = user_profile
        request.session.modified = True  # Asegura que se guarde la sesión