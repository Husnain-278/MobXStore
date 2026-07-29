from django.conf import settings


def set_auth_cookies(response, access_token: str, refresh_token:str):
    """
    Set JWT access and refresh tokens as HttpOnly cookies.
    """
    
    response.set_cookie(
        key= settings.JWT_ACCESS_COOKIE,
        value = access_token,
        max_age= settings.JWT_ACCESS_COOKIE_MAX_AGE,
        httponly = settings.JWT_COOKIE_HTTP_ONLY,
        secure = settings.JWT_COOKIE_SECURE,
        samesite = settings.JWT_COOKIE_SAMESITE,
        path = settings.JWT_ACCESS_COOKIE_PATH,
    )
    
    response.set_cookie(
        key = settings.JWT_REFRESH_COOKIE,
        value = refresh_token,
        max_age = settings.JWT_REFRESH_COOKIE_MAX_AGE,
        httponly = settings.JWT_COOKIE_HTTP_ONLY,
        secure = settings.JWT_COOKIE_SECURE,
        samesite = settings.JWT_COOKIE_SAMESITE,
        path= settings.JWT_REFRESH_COOKIE_PATH,
    )
    
    
def clear_auth_cookies(response):
    response.delete_cookie(
        key=settings.JWT_ACCESS_COOKIE,
        path=settings.JWT_ACCESS_COOKIE_PATH,
    )

    response.delete_cookie(
        key=settings.JWT_REFRESH_COOKIE,
        path=settings.JWT_REFRESH_COOKIE_PATH,
    )
    
    
    
def set_access_cookie(response, access_token:str):
    """
    Set a new access token as an HttpOnly cookie.
    """
    
    
    response.set_cookie(
        key = settings.JWT_ACCESS_COOKIE,
        value = access_token,
        max_age = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
        httponly = settings.JWT_COOKIE_HTTP_ONLY,
        secure = settings.JWT_COOKIE_SECURE,
        samesite = settings.JWT_COOKIE_SAMESITE,
        path = settings.JWT_ACCESS_COOKIE_PATH,
    )
    
    return response