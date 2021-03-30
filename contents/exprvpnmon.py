#! /usr/bin/python3
# monitoring for expressvpn and restarting the connection everytime it wigs out

from os import environ
from time import sleep
from shutil import copyfile
from sys import exit
import subprocess, pexpect, logging

#create logging file
log_location = r'/log/debug.log'
logging.basicConfig(filename=log_location, encoding='utf-8', level=logging.DEBUG)

def check_location(loc):
    """Makes sure the location is valid. I'm just going to list the big ones.
        If this is stopping you from doing something cool, remove it yourself!"""
    valid_locations = ('smart', 'usny', 'ussf', 'usch', 'usda', 'usla2', 'usmi2',
        'usse', 'cato', 'cato2')
    if loc in valid_locations:
        logging.debug('Location valid, returning.')
        return loc
    elif loc == None:
        logging.warning('No location found, picking smart.')
        return 'smart'
    else:
        logging.warning('Invalid or unlisted location, reverting to smart.')
        return 'smart'


def conn_status():
    """Checks, parses and returns status of VPN connection as True or False"""
    result = subprocess.check_output(["expressvpn", "status"])
    if b"Connected" in result:
        logging.info("ExpressVPN connection was checked and is live.")
        if b"A new version" in result:
            logging.warning("ExpressVPN reports there is a new version available.")
        return True
    else:
        logging.warning("ExpressVPN connection was checked and is down.")
        return False


def conn_start():
    """Starts the expressvpn connection"""
    location = check_location(environ.get('LOCATION'))
    result = subprocess.call(["expressvpn", "connect", location])
    if result == 0:
        logging.info("ExpressVPN connection initiated.")
    else:
        logging.critical('An unknown error caused the expressvpn connect command to fail.')


def first_start():
    """Activates VPN, checks for success then starts the connection.
        DNS gets locked during startup so we need to mess around to
        get it to behave."""
    logging.info("Beginning initial startup.")
    if environ.get('ACTIVATION') == None:
        logging.critical('No activation code found. Unable to continue!')
        exit()
    copyfile('/etc/resolv.conf', '/tmp/resolv.conf')
    subprocess.call(['umount', '/etc/resolv.conf'])
    copyfile('/tmp/resolv.conf', '/etc/resolv.conf')
    result = subprocess.check_output(['service', 'expressvpn', 'restart'])
    if b'[ OK ]' in result:
        child = pexpect.spawn('expressvpn activate')
        out = child.expect(
            ["Enter activation code:",
            "Already activated. Logout from your account (y/N)?"])
        if out == 0:
            child.sendline(environ.get('ACTIVATION'))
            child.expect("information.")
            child.sendline('n')
            logging.info("Activation successful!")
        elif out == 1:
            child.sendline('n')
            logging.debug("Activation called but client is already activated.")
        else:
            logging.debug(f"Activation used: {environ.get('ACTIVATION')}")
            logging.critical('Unable to activate ExpressVPN.')
            exit()
        child.expect(pexpect.EOF)
        conn_start()
        sleep(60)


def recovery():
    logging.warning("Attempting to recover ExpressVPN.")
    attempt = 1
    attempt_number = 5
    while attempt < attempt_number:
        conn_start()
        sleep(5 * attempt)
        if conn_status():
            logging.info("ExpressVPN recovered successfully.")
            break
        else:
            attempt += 1
            if attempt >= attempt_number:
                logging.critical("Unable to reconnect ExpressVPN. Exiting script.")
                exit()

#Main loop, activates and connects
#Every 60 seconds, it will check to make sure its connected
#On failure, it runs through the recovery loop
#If the recovery loop can't get the connection back, it terminates the script
#which restarts the container
if __name__ == "__main__":
    first_start()
    while True:
        if conn_status():
            sleep(60)
        else:
            recovery()
