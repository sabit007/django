from datetime import datetime


class RequestLoggerMiddleware:
    """
    Django middleware is just a callable class:
    - __init__ runs ONCE, when the server starts (Django hands it the
      next middleware/view in the chain as `get_response`).
    - __call__ runs on EVERY request.

    The `request` flows down through this into the view, and the
    `response` flows back up through this on the way out. We log
    before calling get_response(request), i.e. before the view runs.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        print("---------------------------------")
        print(f"Time   : {now}")
        print(f"Method : {request.method}")
        print(f"Path   : {request.path}")
        print("---------------------------------")

        response = self.get_response(request)
        return response
