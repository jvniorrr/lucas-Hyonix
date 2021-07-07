import requests, json, typing


class HyonixAPI:
    def __init__(self, token) -> None:
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        

    # server related options
    def getServers(self):
        headers = self.headers
        r = requests.get('https://api.hyonix.com/v1/servers', headers=headers, timeout=20)

        # all servsers that are activate or suspended are returned

        # list for all Active Servers
        active_servers = []

        if r.status_code == 200:
            all_servers = r.json()
            if all_servers:
                for server in all_servers:
                    if server['hyonix_status'] == 'Active':
                        # add server to active ones
                        active_servers.append(server)

            return active_servers

    # return specific server information
    def getServerDetails(self, serverid) -> dict:
        """Method to retrieve information specific to a server
        
        Parameters
        --------
        serverid : str
            - str / integer value representing the server we are looking for
        
        Returns
        ---------
            - Dictionary Object"""
        headers = self.headers
        try:
            r = requests.get(f'https://api.hyonix.com/v1/server/{serverid}', headers=headers, timeout=15)

            if r.status_code == 200:
                server_data = r.json()
            # server_data = json.loads(r.text)

                server = {
                    'server_name':server_data['name'],
                    'server_ip': server_data['dedicatedip'],
                    'server_id': server_data['id'],
                    'next_due_date': server_data['nextduedate'],
                    'package': server_data['packagename'],
                    'location': server_data['location']['code']
                }

                return server

        except json.JSONDecodeError:
            print("Error occured retrieving the json data from API.")
            server = None
            return server
        except Exception as e:
            print("Error occured retrieving server details.", e)
            server = None
            return server


    def serverRestart(self, serverid) -> bool:
        """Method to reset / restart a specified server
        
        Parameters
        ---------
        serverid : int
            - int value associated with specified server being reset
        Returns
        ----------
            - Bool"""
        headers = self.headers
        # headers['power_action'] = 'reset' # combination of a hard shutdown/reset & a start up.
        data = {'power_action': 'reset'}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        #  await a call to api and reboot of machine
        try:

            r = requests.post(f'https://api.hyonix.com/v1/server/{serverid}/power', headers=headers, params=data, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "successfully reset" in data["message"].lower():
                    return True

        except json.JSONDecodeError:
            print("Error occured retrieving the json data from API.")
            return False

        except Exception as e:
            print("Error occured restarting users server.", e)
            return False

        # print(r.text)

    def resetPassword(self, serverid):
        """Method to reset password for specified server id
        
        Parameters
        ----------
        serverid : int
            - int value associated with server. UUID
        Returns
        --------"""
        headers = self.headers

        PASSWORD = ""

        try:

            r = requests.put(f'https://api.hyonix.com/v1/server/{serverid}/resetpassword', headers=headers, timeout=20)
            if r.status_code == 200:
                data = r.json()
                if "password reset request has been successfully sent" in data["message"].lower():
                    # print(f"Password was changed for server {serverid}")
                    PASSWORD = data["password"]
                    return PASSWORD, True
        except json.JSONDecodeError:
            print("Error occured retrieving the json data from API.")
            return PASSWORD, False
        except Exception as e:
            print("Error occured resetting password.", e)
            return PASSWORD, False


if __name__ == '__main__':
    pass