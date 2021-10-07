
try:
    from Requests.gateway_requests import GatewayRequests

except ModuleNotFoundError:
    from .gateway_requests import GatewayRequests


class Postman(object):

    def __init__(self):
        self.gateway_requests = GatewayRequests()