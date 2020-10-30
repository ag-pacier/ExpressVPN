#! /usr/bin/python3
# monitoring for expressvpn and restarting the connection everytime it wigs out

from os import environ
from time import sleep
from shutil import copyfile
from sys import exit
import subprocess, pexpect

def check_location(loc):
    """Makes sure the location is valid. I'm just going to list the big ones.
        If this is stopping you from doing something cool, remove it yourself!"""
    valid_locations = ('smart', 'usny', 'ussf', 'usch', 'usda', 'usla2', 'usmi2',
        'usse', 'cato', 'cato2')
    if loc in valid_locations:
        return loc
    elif loc == None:
        print('No location found, picking smart.')
        return 'smart'
    else:
        print('Invalid location, reverting to smart.')
        return 'smart'


def conn_status():
    """Checks, parses and returns status of VPN connection as True or False"""
    result = subprocess.check_output(["expressvpn", "status"])
    if b"Connected" in result:
        print("ExpressVPN connection was checked and is live.")
        if b"A new version" in result:
            print("ExpressVPN reports there is a new version available.")
        return True
    else:
        print("ExpressVPN connection was checked and is down.")
        return False


def conn_start():
    """Starts the expressvpn connection"""
    location = check_location(environ.get('LOCATION'))
    result = subprocess.call(["expressvpn", "connect", location])
    if result == 0:
        print("ExpressVPN connection initiated.")
    else:
        exit('Something has gone wrong. Terminating.')


def first_start():
    """Activates VPN, checks for success then starts the connection.
        DNS gets locked during startup so we need to dick around to
        get it to behave."""
    if environ.get('ACTIVATION') == None:
        exit('No activation code set, please set and run again.')
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
        elif out == 1:
            child.sendline('n')
        else:
            print(environ.get('ACTIVATION'))
            exit("Unable to activate ExpressVPN.")
        child.expect(pexpect.EOF)
        conn_start()
        sleep(60)


def recovery():
    print("Attempting to recover ExpressVPN.")
    attempt = 1
    attempt_number = 5
    while attempt < attempt_number:
        conn_start()
        sleep(5 * attempt)
        if conn_status():
            print("ExpressVPN recovered successfully.")
            break
        else:
            attempt += 1
            if attempt >= attempt_number:
                print(
                    "Unable to reconnect ExpressVPN.")
                exit(
                    "Terminating monitor script.")


first_start()
while True:
    if conn_status():
        sleep(60)
    else:
        recovery()
