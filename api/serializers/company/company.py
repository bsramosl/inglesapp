from rest_framework import serializers

from app.models import Company


class CompanySerializer(serializers.ModelSerializer):
    iconUrl = serializers.SerializerMethodField()
    bannerUrl = serializers.SerializerMethodField()

    def get_iconUrl(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.icon.url)

    def get_bannerUrl(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.banner.url)

    class Meta:
        model = Company
        fields = [
            'name', 'slogan', 'description', 'email', 'phone',
            'facebook', 'twitter', 'instagram', 'linkedin',
            'iconUrl', 'bannerUrl'
        ]