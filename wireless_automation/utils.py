import re
import socket
from typing import Union, Text
from wireless_automation.exceptions import ValidationIPAddressError


def check_validation_ip(ip_address: Text) -> Union[Text, ValidationIPAddressError]:
    """
    Check Validation IP Address with regex if true return IP address else raise an exception
    :param ip_address: get ip address in a string type
    :return: IP Address if IP address is valid
    """
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    if not re.search(regex, ip_address):
        raise ValidationIPAddressError(ip_address=ip_address)
    else:
        return ip_address


def get_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP
