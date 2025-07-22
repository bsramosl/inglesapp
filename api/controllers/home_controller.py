from rest_framework import viewsets, status

from api.serializers.company.company import CompanySerializer
from app.models import ModuleCategory, TopicCategory, Company, Module
from utils.respose import UtilResponse
from rest_framework.permissions import AllowAny


class NavBarViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        eData = {}
        uResponse = UtilResponse()
        try:
            is_authenticated = request.user.is_authenticated
            menu_data = self.menu_data(request, is_authenticated)
            return uResponse.response_success(data=menu_data)
        except Exception as ex:
            return uResponse.response_error(
                message=str(ex),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def menu_data(self, request, is_authenticated):
        data = {
            'menu': self.menu_options(is_authenticated, request.user),
            # 'user_info': self._get_user_info(request.user) if is_authenticated else None
        }
        return data

    def menu_options(self, is_authenticated, user):
        return self.build_menu(authenticated=is_authenticated)

    def build_menu(self, authenticated: bool):
        accessible_modules = (
            Module.objects
            .filter(api=True, authenticated= authenticated, is_active=True, status=True)
            .select_related('category')
            .order_by('category__order', 'order')
            .distinct()
        )

        categories_dict = {}
        for module in accessible_modules:
            category = module.category
            cat_id = category.id

            if cat_id not in categories_dict:
                categories_dict[cat_id] = {
                    "id": cat_id,
                    "name": category.name,
                    "icon": category.icon or 'bx-home-circle',
                    "order": category.order,
                    "modules": []
                }

            categories_dict[cat_id]["modules"].append({
                "id": module.id,
                "name": module.name,
                "icon": module.icon or 'bx-circle',
                "url": module.url,
                "order": module.order
            })

        return sorted(categories_dict.values(), key=lambda c: c['order'])

class HomeViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        eData = {}
        uResponse = UtilResponse()
        try:
            categories = TopicCategory.objects.filter(
                is_active=True
            ).order_by('order')

            categories_data = [{
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'order': category.order
            } for category in categories]

            eData['categories'] = categories_data
            eData['menu'] = ''
            eData['homeContent'] = ''
            return uResponse.response_success(data=eData)
        except Exception as ex:
            return uResponse.response_error(message=str(ex),status=status.HTTP_500_INTERNAL_SERVER_ERROR)