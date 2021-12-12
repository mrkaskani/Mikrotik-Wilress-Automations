from routeros_api import RouterOsApiPool


class Authentication:
    """
    use context manager to control resources for connect and disconnected from device
    """

    def __init__(self, ip: str, username: str, password: str):
        """
        create an connection to read and write with API
        :param ip: this is host ip that we want to connect
        :param username: username of host
        :param password: password of host
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.plaintext_login = False
        self.connection = RouterOsApiPool(self.ip, username=self.username, password=self.password,
                                          plaintext_login=self.plaintext_login)

    def __enter__(self):
        """
        create API connection from the session that we created in constructor
        :return API connection:
        """
        return self.connection.get_api()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        disconnect the session
        :return if connection is open then close it:
        """
        if self.connection.get_api():
            return self.connection.disconnect()
