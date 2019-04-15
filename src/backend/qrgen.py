import io

import pyqrcode
from django.http import HttpResponseNotFound, HttpResponse

from backend.models import TGUser
from backend.tgbot.utils import get_public_host
from bot import settings

_PUBLIC_HOST = get_public_host()
_PUBLIC_PORT = settings.PUBLIC_PORT


def qr_code_view(request, user_id):
    user: TGUser = TGUser.objects.filter(id=user_id, is_authorized=True).first()
    if user is None:
        return HttpResponseNotFound('No such user')
    qr = pyqrcode.create(
        f'{user.last_checked_email}\n{user.name} {user.last_name} {user.username}\n{get_qr_code_url(user)}')
    buffer = io.BytesIO()
    qr.png(buffer, scale=10)
    read = buffer.getvalue()
    return HttpResponse(read, content_type="image/png")


def get_qr_code_url(user: TGUser):
    return f'http://{_PUBLIC_HOST}:{settings.PUBLIC_PORT}/qr/{user.id}'
