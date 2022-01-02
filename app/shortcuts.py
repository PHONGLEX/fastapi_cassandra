from .config import get_settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse


settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))


def redirect(path, cookies:dict={}, remove_session=False):
    response = RedirectResponse(path, status_code=302)
    for k, v in cookies.items():
        response.set_cookie(key=k, value=v, httponly=True)
    if remove_session:
        response.set_cookie(key="session_ended", value=1, httponly=True)
        response.delete_cookie('session_id')
    return response
 
 
def render(request, template_name, context, status_code:int=200, cookies:dict={}):
    ctx = context.copy()
    ctx.update({"request": request})
    t = templates.get_template(template_name)
    html_str = t.render(ctx)
    response = HTMLResponse(html_str, status_code=status_code)
    
    if len(cookies.keys()) > 0:
        for k,v in cookies.items():
            response.set_cookie(key=k, value=v, httponly=True)
    
    return response