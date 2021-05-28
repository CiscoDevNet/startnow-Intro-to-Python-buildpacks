#!/usr/bin/env python
"""
Main python file that calls app.aci_conn.ConnectACI
"""
import datetime
import argparse
import json
import os
import sys
from urllib.parse import urlparse
from app.aci_conn import ConnectACI
import app.aci_webex as webex


def main(url, username, password, webex_token=None, webex_room=None):
    """
    POST logins into APIC and Prints Status Update
        Arguments:
            url (str): url of APIC
            username (str): APIC api username
            password (str): APIC api password
            message (str): Str message to be sent
            webex_token (cls): Api token for future requests
            webex_room (str): Name of webex room
            webex_email (str): Email to be added to the webex room
        return: None
    """
    aci = ConnectACI(url, username, password)
    tenants = aci.get_tenant()['imdata']
    tenant_count = len(tenants)
    health = aci.get_aci_health()
    old_tenants = get_old_tenant()
    webex_card = create_webex_card()
    if webex_token:
        token = webex.get_webex_token(webex_token)
        webex.send_webex_message(token, webex_room=webex_room, webex_card=webex_card)
    else:
        get_aci_stats(aci.username, tenant_count, tenants,
                      health, old_tenants)
    update_log(tenants)

def get_aci_stats(name, tenant_count, tenants, health, old_tenants):
    """
    POST logins into APIC and Prints Status Update
        Arguments:
            name (str): APIC username
            tenant_count (int): Number of ACI tenants
            tenants (dict): ACI tenant dict
            health (dict): ACI health dict
            old_tenants (list): List of logged ACI tenants
            current_time (str): Today's datetime
        return: None
    """
    current_time = get_date()
    null_tenant = 0
    print("\n")
    print("#" * 10 + " APIC STATUS UPDATE " + "#" * 13)
    print(f" ✅ {name} Logged in at: " + current_time + "\n")
    print("\n- FabricOverallHealth:")
    if len(health['imdata']) >  0:
        print(" " * 12 +
        "healthAvg: "\
        f"{health['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthAvg']}")
        print(" " * 12 +
        "healthMax: "\
        f"{health['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthMax']}")
        print(" " * 12 +
        "healthMin: "\
        f"{health['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthMin']}\n")
    else:
        print(" " * 12 + "Data Not Found")
    print("- List of New Tenants: ")
    for i in tenants:
        if i['fvTenant']['attributes']['name'] not in old_tenants:
            print(" " * 12 + f"{i['fvTenant']['attributes']['name']} **NEW-TENANT**")
            null_tenant += 1
        else:
            print(" " * 12 + f"{i['fvTenant']['attributes']['name']}")
    if null_tenant == 0:
        print(" " * 12 + "*NO NEW TENANTS*\n")
    print(f"- Tentant Count: {tenant_count}")
    print("#" * 44 + "\n")

def create_webex_card():
    """
    Method creates adaptive card for webex message
        return: Webex card message
        rtype: dict
    """
    with open("./cards/card.json") as temp_v:
        cards = json.load(temp_v)
    return cards

def get_old_tenant():
    """
    Method returns list of logged ACI Tenants
        rtype: list
    """
    old_tenants = []
    with open("tenant_log.txt", "r") as file:
        old_tenants = file.read().splitlines()
    return old_tenants

def update_log(tenants):
    """
    Method updates tenant_log.txt
        Arguments:
            tenants (str):
    """
    with open("tenant_log.txt", "w") as file:
        for tenant in tenants:
            file.write(f"{tenant['fvTenant']['attributes']['name']}\n")

def get_date():
    """
    GET Current Date and Time
        return: Date/time '03-05-2021 12:04'
        rtype: str
    """
    return datetime.datetime.now().strftime('%m-%d-%Y %H:%M')

def validate_url(url):
    """
    Method validates http url
        Arguments:
            url (str): Address of APIC 'http://' or 'https://'
            rtype: None
    """
    valid_url = {"http", "https"}
    result = urlparse(url)
    if result.scheme not in valid_url:
        sys.exit("Please enter APIC url in 'http(s)://www.cisco.com' format.")


if __name__ == "__main__":
    # Argparse grabs commandline arguments
    # Defaults to DevNet ACI Always on Sandbox Creds
    parser = argparse.ArgumentParser(description="Arguments: url, username, password,"\
                                     " webex_token, webex_room")
    parser.add_argument("--url", help="Optional argument to pass url or ip of APIC"\
                        "\nDefault: 'https://sandboxapicdc.cisco.com'")
    parser.add_argument("--username", help="Optional argument to pass username for APIC user"\
                        "\nDefault: 'admin'")
    parser.add_argument("--password", help="Optional argument to pass password for FMC user"\
                        "\nDefault: 'ciscopsdt'")
    parser.add_argument("--webex_token", help="Optional argument to pass webex api token")
    parser.add_argument("--webex_room", help="Optional argument to pass webex room name"\
                        "\n***NOTE*** arg must be passed with token")
    args = parser.parse_args()
    args = vars(args)
    if args['url'] is None:
        if 'url' in os.environ:
            args['url'] = os.environ['url']
        else:
            args['url'] = "https://sandboxapicdc.cisco.com"
    validate_url(args['url'])
    if args['username'] is None:
        if 'username' in os.environ:
            args['username'] = os.environ['username']
        else:
            args['username'] = "admin"
    if args['password'] is None:
        if 'password' in os.environ:
            args["password"] = os.environ['password']
        else:
            args['password'] = "ciscopsdt"
    if args['webex_token'] is None:
        if 'webex_token' in os.environ:
            args['webex_token'] = os.environ['webex_token']
    if args['webex_token']:
        if args['webex_room'] is None:
            if 'webex_room' in os.environ:
                args['webex_room'] = os.environ['webex_room']
            else:
                print("Please pass in 'webex_token' and 'webex_room' args")
                sys.exit("For more info see 'main.py --help'")
    main(**args)
