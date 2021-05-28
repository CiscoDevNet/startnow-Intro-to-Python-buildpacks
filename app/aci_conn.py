#!/usr/bin/env python
"""
Python Class for authenticate and gather data in Cisco ACI
"""
import json
import sys
import requests


class ConnectACI:
    """POST logins into APIC and Returns Token
            Arguments:
                url (str): url of APIC
                username (str): APIC api username
                password (str): APIC api password
            type data: str
            return: Return the APIC token
            rtype: str
    """
    def __init__(self, url, username, password):
        self.username = username
        self.password = password
        self.url = url
        self.token = self.get_token()

    def get_token(self):
        """POST logins into APIC and Returns Token
            return: Return the APIC token
            rtype: str
        """
        payload = {
            "aaaUser": {
                "attributes": {
                    "name": self.username,
                    "pwd": self.password
                    }
                }
            }
        headers = {"Content-Type": "application/json"}
        response = requests.request('POST', self.url + "/api/aaaLogin.json",
                                    headers=headers, json=payload)
        if response.status_code == 200:
            json_data = json.loads(response.text)
        else:
            if response.status_code == 401:
                sys.exit(f"Login failed: {response.status_code}\n- Bad username or password\n"\
                "- Check credentials and try again.")
        return "APIC-cookie=" + json_data['imdata'][0]['aaaLogin']['attributes']['token']

    def get_tenant(self):
        """GET created ACI tenants
            return: Return the APIC tenants
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        url = self.url + "/api/class/fvTenant.json"
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)

    def get_subnet(self):
        """GET created ACI Subnets
            return: Return the ACI subnets
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        url = self.url + "/api/class/fvSubnet.json"
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)

    def get_aci_health(self):
        """GET created ACI Fabric Health
            return: Return the ACI health
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        url = self.url + "/api/node/mo/topology/HDfabricOverallHealth5min-0.json"
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)

    def get_aci_faultinfo(self):
        """GET created ACI Fabric Health
            type data: str
            return: Return the ACI fault info
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        url = (self.url + '/api/node/class/faultInfo.json?' +
            'query-target-filter=and(ne(faultInfo.severity,"cleared"))' +
            '&order-by=faultInfo.severity|desc&page=1&page-size=15')
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)

    def get_crc_errors(self):
        """GET created ACI CRC Errors
            type data: str
            return: Return the APIC crc errors
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        url = (self.url + '/api/node/class/rmonEtherStats.json?' +
            'query-target-filter=and(gt(rmonEtherStats.cRCAlignErrors,"0")')
        response = requests.request("GET", url, headers=headers)
        return json.loads(response.text)

    def create_tenant(self, tenant_name):
        """POST create ACI tenant
            Args:
                tenant_name (str): Name of tenant
            return: Return the APIC tenants
            rtype: dict
        """
        headers = {
            "Content-Type": "application/json",
            "Cookie": self.token
            }
        payload = {
            "fvTenant" : {
                "attributes" : {
                    "name": f"{tenant_name}"
                    }
                }
            }
        url = (self.url + '/api/mo/uni.json')
        response = requests.post(url, headers=headers, json=payload)
        return json.loads(response.text)
