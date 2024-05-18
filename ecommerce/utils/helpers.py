def get_current_host(request):
    protocol = request.is_secure() and 'http' or 'https'
    host = request.get_host()
    return f"{protocol}://{host}/"