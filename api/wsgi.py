from index import app
from werkzeug.middleware.proxy_fix import ProxyFix

application = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)