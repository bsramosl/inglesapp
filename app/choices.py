class ActionTypeUserToken:
    LOGIN = 1
    API_ACCESS = 2
    PASSWORD_RESET = 3

    CHOICES = (
        (LOGIN, 'LOGIN'),(API_ACCESS, 'API_ACCESS'),(PASSWORD_RESET,'PASSWORD_RESET'))


class Priorities:
    ALTA = 1
    MEDIA = 2
    BAJA = 3
    CHOICES = ((ALTA, 'ALTA'),(MEDIA, 'MEDIA'),(BAJA, 'BAJA'))

class Types:
    MESSAGE = 1
    PROCESS = 2
    INFORMATION = 3
    CHOICES = ((MESSAGE, 'MESSAGE'),(PROCESS, 'PROCESS'),(INFORMATION, 'INFORMATION'))