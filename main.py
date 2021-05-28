#!/usr/bin/env python
"""
Main python file that calls app.aci_conn.ConnectACI
"""
import datetime
import argparse
import sys
from urllib.parse import urlparse
from app.aci_conn import ConnectACI


def main(url, username, password):
    """
    POST logins into APIC and Prints Status Update
        Arguments:
            url (str): url of APIC
            username (str): APIC api username
            password (str): APIC api password
        return: None
    """
    aci = ConnectACI(url, username, password)
    tenants = aci.get_tenant()['imdata']
    tenant_count = len(tenants)
    health = aci.get_aci_health()
    old_tenants = get_old_tenant()
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
    result = urlparse(url)
    if result.scheme != "http" or result.scheme != "https":
        sys.exit("Please enter APIC url in 'http(s)://www.cisco.com' format.")


if __name__ == "__main__":
    # Argparse grabs commandline arguments
    # Defaults to DevNet ACI Always on Sandbox Creds
    parser = argparse.ArgumentParser(description="Pass ACI url, username, password")
    parser.add_argument("--url", help="Optional argument to pass url or ip of APIC\
                        Default: 'https://sandboxapicdc.cisco.com'")
    parser.add_argument("--username", help="Optional argument to pass username for APIC user\
                        Default: 'admin'")
    parser.add_argument("--password", help="Optional argument to pass password for FMC user\
                        Default: 'ciscopsdt'")
    args = parser.parse_args()
    if args.url is None:
        args.url = "https://sandboxapicdc.cisco.com"
    else:
        validate_url(args.url)
    if args.username is None:
        args.username = "admin"
    if args.password is None:
        args.password = "ciscopsdt"
    main(args.url, args.username, args.password)
