from starlette.exceptions import HTTPException

from .main import app
from .shortcuts import render


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    status_code = exc.status_code
    template_name = "errors/main.html"
    context = {"status_code": status_code}
    return render(request, template_name, context, status_code)