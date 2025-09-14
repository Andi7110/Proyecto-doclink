from django.shortcuts import render
from django.http import HttpResponseForbidden

def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view to provide more detailed error information
    """
    return HttpResponseForbidden(
        f"CSRF verification failed. Request aborted.\n"
        f"Reason: {reason}\n"
        f"Origin: {request.META.get('HTTP_ORIGIN', 'Not provided')}\n"
        f"Referer: {request.META.get('HTTP_REFERER', 'Not provided')}\n"
        f"Host: {request.META.get('HTTP_HOST', 'Not provided')}\n"
        f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Not provided')}"
    )
