from django.contrib.auth import authenticate, login

def set_cookie(request, key, val):
    setattr(request, '__cookies_to_set__', 
            getattr(request, '__cookies_to_set__', {}))
    request.__cookies_to_set__[key] = val

def delete_cookie(request, key):
    setattr(request, '__cookies_to_delete__', 
            getattr(request, '__cookies_to_delete__', []))
    request.__cookies_to_delete__.append(key)

class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.__class__.set_cookie = set_cookie
        request.__class__.delete_cookie = delete_cookie
        if (request.method == "POST" 
            and "__ac_name" in request.POST 
            and "__ac_password" in request.POST):
            user = authenticate(username=request.POST['__ac_name'],
                                password=request.POST['__ac_password'])
            if user is not None:
                login(request, user)
        return None

    def process_response(self, request, response):
        if hasattr(request, '__cookies_to_set__'):
            for key, val in request.__cookies_to_set__.items():
                response.set_cookie(key, val)
        if hasattr(request, '__cookies_to_delete__'):
            for key in request.__cookies_to_delete__:
                response.delete_cookie(key)
        return response
