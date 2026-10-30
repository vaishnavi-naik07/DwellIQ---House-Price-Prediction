import sys
from pathlib import Path
import backend.auth.auth_service as _auth_svc

# Forward all auth functions to backend.auth.auth_service for seamless backward compatibility
from backend.auth.auth_service import (
    register_user,
    authenticate_user,
    hash_password,
    verify_password,
    validate_email,
    validate_password_strength,
    check_rate_limit,
    record_failed_attempt,
    clear_failed_attempts,
    save_user_estimation,
    get_user_estimations,
    init_auth_db,
    get_db_connection,
    PBKDF2_ITERATIONS,
    SALT_BYTES,
    RATE_LIMIT_WINDOW_SEC,
    MAX_FAILED_ATTEMPTS,
    FAILED_ATTEMPTS,
    EMAIL_REGEX,
)

# Custom property proxy so setting src.auth.DB_PATH dynamically updates backend.auth.auth_service.DB_PATH
class _AuthModuleProxy(sys.modules[__name__].__class__):
    @property
    def DB_PATH(self):
        return _auth_svc.DB_PATH

    @DB_PATH.setter
    def DB_PATH(self, val):
        _auth_svc.DB_PATH = val

sys.modules[__name__].__class__ = _AuthModuleProxy

__all__ = [
    "register_user",
    "authenticate_user",
    "hash_password",
    "verify_password",
    "validate_email",
    "validate_password_strength",
    "check_rate_limit",
    "record_failed_attempt",
    "clear_failed_attempts",
    "save_user_estimation",
    "get_user_estimations",
    "init_auth_db",
    "get_db_connection",
    "DB_PATH",
    "PBKDF2_ITERATIONS",
    "SALT_BYTES",
    "RATE_LIMIT_WINDOW_SEC",
    "MAX_FAILED_ATTEMPTS",
    "FAILED_ATTEMPTS",
    "EMAIL_REGEX",
]
