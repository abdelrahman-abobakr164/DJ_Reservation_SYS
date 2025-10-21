from functools import wraps
from django.http import Http404
from django.shortcuts import get_object_or_404


def authenticated_and_owner(model):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            model_obj = get_object_or_404(model, username=kwargs.get("username"))
            if request.user.username == model_obj.username:
                return view_func(request, *args, **kwargs)
            else:
                return Http404()
        return _wrapped_view

    return decorator
