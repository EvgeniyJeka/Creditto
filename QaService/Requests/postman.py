from Requests.gateway_requests import GatewayRequests
from credittomodels import Offer



class Postman(object):

    def __init__(self):
        self.gateway_requests = GatewayRequests()