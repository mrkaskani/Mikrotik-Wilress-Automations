class IpAddressError(Exception):
    def __init__(self, ip_address):
        super(IpAddressError, self).__init__(ip_address)
        self.ip_address = ip_address


class ValidationIPAddressError(IpAddressError):
    pass
