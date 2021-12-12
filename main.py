from wireless_automation.automation import Automation
from wireless_automation.utils import check_validation_ip, get_ip
from wireless_automation.exceptions import ValidationIPAddressError
from routeros_api.exceptions import RouterOsApiConnectionError, RouterOsApiCommunicationError
from getpass import getpass
import logging
import sys


class Menu:
    """Display a menu and respond to choices when run."""

    def __init__(self):
        self.choices = {
            '1': self._show_logs,
            '2': self._clear_logs,
            '3': self._run_automation,
            '4': self._quit,
        }
        self.config = {
            'level': logging.INFO,
            'filename': 'app.log',
            'filemode': 'a+',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
        logging.basicConfig(**self.config)

    @staticmethod
    def _display_menu():
        """show Menu"""
        print("\nProgram Menu\n\n1. Show Logs\n2. Clear Logs\n3. Run Automation\n4. Quit\n")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input("Enter an Option: ")
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print(f"{choice} is not a valid choice")

    @staticmethod
    def _show_logs():
        """ show all logs """
        try:
            with open("app.log", 'r') as file_handler:
                logs = file_handler.read()
                print(logs)
        except IOError as e:
            logging.error(msg=e)

    @staticmethod
    def _clear_logs():
        """ clear all logs """
        try:
            with open("app.log", 'r+') as file_handler:
                file_handler.truncate(0)
                print("*** Logs Successfully Cleared ***")
                logging.info(msg="*** Logs Successfully Cleared ***")
        except IOError as e:
            logging.error(msg=e)

    @staticmethod
    def _run_automation():
        try:
            ip_address = input("Please Enter IP Address: ")
            check_validation_ip(ip_address)
            username = input("Username: ")
            password = getpass(prompt='Password: ', stream=None)
            logging.info(msg=f"{get_ip()} login to {ip_address}, the process is starting")
            automation = Automation(ip=ip_address, username=username, password=password)
            automation.set_freq()
        except ValidationIPAddressError as e:
            logging.error(msg=f"{e.ip_address} is invalid ip address")
            print(f"{e.ip_address} is invalid")
        except RouterOsApiConnectionError as e:
            logging.error(msg=e)
            print(e)
        except RouterOsApiCommunicationError as e:
            logging.error(msg=e)
            print(e)
        else:
            print("*** Automation Successfully Done ***")
        finally:
            logging.info(msg=f"{get_ip()}  the process has been finished")
            print("the process has been finished")

    @staticmethod
    def _quit():
        print("Thank you for using")
        sys.exit(0)


if __name__ == '__main__':
    Menu().run()
