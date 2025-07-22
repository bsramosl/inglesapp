from rest_framework import status
from rest_framework.response import Response

from utils.messages import ACTION_SUCCESS,ERROR_ACTION

class UtilResponse:

    def response_success(self, data=[], message=ACTION_SUCCESS):

        response_data = {
            'success': True,
            'message': message,
            'data': data
        }
        return Response(response_data, status=status.HTTP_200_OK)

    def response_success_list(self, data=[],choices=[], message=ACTION_SUCCESS):

        response_data = {
            'success': True,
            'message': message,
            'choices': choices,
            'data': data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


    def response_error(self, message=ERROR_ACTION, errors={}, status=status.HTTP_400_BAD_REQUEST):

        response_data = {
            'success': False,
            'message': message,
            'errors': errors,
        }
        return Response(response_data, status)