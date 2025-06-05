class ActionTypeUserToken:
    LOGIN = 1
    API_ACCESS = 2
    PASSWORD_RESET = 3

    CHOICES = (
        (LOGIN, 'LOGIN'),
        (API_ACCESS, 'API_ACCESS'),
        (PASSWORD_RESET,'PASSWORD_RESET')
    )