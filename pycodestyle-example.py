'''
Example of a script that executes a CLI command on a remote device over established SSH connection.
Administrator login options and CLI commands are device specific, thus this script needs to be adapted to a concrete device specifics.
    Current script assumes interaction with Cisco IOS device.
NOTES: Requires installation of the 'paramiko' Python package using: pip install paramiko
        The 'paramiko' package is documented at: http://docs.paramiko.org
        Complete set of SSH client operations is available at: http://docs.paramiko.org/en/1.15/api/client.html
pydoc-example.py
'''

# Built-in required modules/packages/library
import time

# Third-party required modules/packages/library
import pexpect

# Variables/data
ip_address = '192.168.56.101'
username = 'prne'
password = 'cisco123!'
password_enable = 'class123!'
config=['hostname R10', 'hostname R1']

# Functions
def connect(ip_address, username, password):
    '''
    Connects to device using pexpect.
    :ip_address: The IP address of the device we are connecting to
    :username: The username that we should use when logging in
    :password: The password that we should use when logging in
    =return: pexpect session object if successful, 0 otherwise
    '''

    print('--- attempting SSH to: ' + ip_address + '\n' +
           '    with the user: ' + username)

    ssh_newkey = 'Are you sure you want to continue connecting'
    session = pexpect.spawn('ssh '+ username + '@' + ip_address, 
                            encoding='utf-8', timeout=20)

    result = session.expect([ssh_newkey, 'Password:', pexpect.TIMEOUT, pexpect.EOF])
    
    # Check for new key/failure
    if result == 0:
        print('New SSH key, accepting!')
        session.sendline('yes')
        result = session.expect([ssh_newkey, 'Password:', pexpect.TIMEOUT, pexpect.EOF])
    elif result != 1:
        print('--- FAILURE! creating session for: ', ip_address)
        return 0

    time.sleep(1)
    print('--- Entering password')

    # Session expecting password, enter details
    session.sendline(password)
    result = session.expect(['>', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if exists then display error and exit
    if result != 0:
        print('--- FAILURE! entering password: ', password)
        return 0
    elif result == 0:
        print('    Successfully entered password')

    return session  # return pexpect session object to caller


def enable_mode(session):
    '''
    Changes the device to privilged exec mode.
    :session: The pexpect session object that we are using
    =return: Print message if successful, 0 otherwise
    '''
    
    print('--- Entering privilged exec mode')

    # Enter privilged exec mode
    session.sendline('enable')
    result = session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if exists then display error and exit
    if result != 0:
        print('--- Failure! entering enable command')
        return 0

    # Send enable password details
    session.sendline(password_enable)
    result = session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if exists then display error and exit
    if result != 0:
        print('--- Failure! entering privilged exec mode')
        return 0

    return print('    Successfully entered priviledged exec mode')


def config_mode(session):
    """
    Runs 'configure terminal' command on device and returns output from device in a string.
    :session: The pexpect session for communication with device
    =return: Print message if successful, 0 otherwise
    """

    print('--- Entering configuration mode')

    # Enter configuration mode
    session.sendline('configure terminal')
    result = session.expect([r'.\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if exists then display error and exit
    if result != 0:
        print('--- Failure! entering config mode')
        return 0

    return print('    Successfully entered configuration mode')


def new_configuration(session,configure):
    '''
    Changes the device configuration.
    :session: The pexpect session object that we are using
    :configure: The command used from the config list
    =return: Print message if successful, 0 otherwise
    '''

    print('--- Modifying configuration')

    # Change the device configuration
    session.sendline(configure)
    result = session.expect([r'\(config\)#', pexpect.TIMEOUT, pexpect.EOF])

    # Check for error, if exists then display error and exit
    if result != 0:
        print('--- Failure! setting configuration')
        return 0

    # Exit config mode
    session.sendline('exit')

    # Exit enable mode
    session.sendline('exit')

    print('    Configuration successfully changed: ' + configure)


# Main program: connect to device, show interface, display
if __name__ == '__main__':

    session = connect(ip_address, username, password)
    if session == 0:
        print('--- Session attempt unsuccessful, exiting.')
        exit()

    enable_mode(session)
    config_mode(session)
    new_configuration(session,config[1])

    # Display device information that configuration was applied
    print('------------------------------------------------------')
    print('')
    print('--- Success! connecting to: ', ip_address)
    print('---               Username: ', username)
    print('---               Password: ', password)
    print('')
    print('------------------------------------------------------')

    # Close the session
    session.sendline('quit')
    session.kill(0)
