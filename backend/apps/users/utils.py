import random
import string
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def generate_verification_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get('request')
    lang = 'fr'
    if request and hasattr(request, 'user') and hasattr(request.user, 'preferred_language'):
        lang = request.user.preferred_language

    if response is not None:
        errors = response.data
        if lang == 'en':
            message = 'An error occurred. Please try again.'
        else:
            message = 'Une erreur est survenue. Veuillez réessayer.'

        if isinstance(errors, dict):
            first_key = next(iter(errors), None)
            if first_key:
                first_error = errors[first_key]
                if isinstance(first_error, list):
                    message = str(first_error[0])
                else:
                    message = str(first_error)

        response.data = {
            'success': False,
            'message': message,
            'errors': errors,
        }
    return response


def api_response(data=None, message_fr='Succès', message_en='Success',
                 success=True, status_code=status.HTTP_200_OK, lang='fr'):
    message = message_fr if lang == 'fr' else message_en
    payload = {
        'success': success,
        'message': message,
    }
    if data is not None:
        payload['data'] = data
    return Response(payload, status=status_code)
