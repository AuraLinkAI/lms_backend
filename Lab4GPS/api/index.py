from Lab4GPS.wsgi import application  # make sure this path is correct
from vercel_wsgi import handle_request

def handler(event, context):
    return handle_request(application, event, context)
