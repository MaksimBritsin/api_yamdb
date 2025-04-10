import random
import string


def get_confirmation_code():
    """Генерирует 6-значный код подтверждения."""
    return ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=6))
