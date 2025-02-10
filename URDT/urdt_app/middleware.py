# urdt_app/middleware.py

from django.shortcuts import render
from django.http import Http404
from django.core.exceptions import PermissionDenied

class GlobalErrorAndNoCacheMiddleware:
    """
    This middleware combines two features:
    
    1. It sets HTTP headers to disable browser caching on every response.
    2. It catches every error response (HTTP status code >= 400) or any unhandled exception,
       and renders a single error template (errors/error.html) with the error code and a message.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request and catch exceptions
        try:
            response = self.get_response(request)
        except Exception:
            # If an exception occurs, render the error template with a 500 status.
            context = {
                'error_code': 500,
                'error_message': "Internal server error. Please login again."
            }
            return render(request, "errors/error.html", context, status=500)

        # If the view returned a response with an error status code (>= 400),
        # override it with our custom error page.
        if response.status_code >= 400:
            code = response.status_code
            # Customize the error message as desired.
            if code == 404:
                msg = "Page not found."
            elif code == 403:
                msg = "Access forbidden."
            elif code == 400:
                msg = "Bad request."
            else:
                msg = "Something went wrong."
            context = {
                'error_code': code,
                'error_message': f"{msg} Please login again."
            }
            # Render our single error template with the proper HTTP status.
            response = render(request, "errors/error.html", context, status=code)

        # Set headers to prevent caching.
        response['Cache-Control'] = "no-store, no-cache, must-revalidate, max-age=0"
        response['Pragma'] = "no-cache"
        response['Expires'] = "0"
        return response
