#!/usr/bin/env python
"""
Script leverages the WebexTeamssdk
Sends a webex teams message
Will create room if not created
Deletes a supplied webex room
To obtain a webex token https://developer.webex.com/
"""
from webexteamssdk import WebexTeamsAPI


def get_webex_token(webex_access_token):
    """
    Get developer webex token to be used for future request
        Arguments:
            webex_access_token (str): Webex developer api token
            return: Return API Token
            rtype: obj
    """
    return WebexTeamsAPI(webex_access_token)

def send_webex_message(webex_token, webex_room, webex_email=None, 
                       webex_message=None, webex_card=None):
    """
    Send a message to a supplied webex room
    Creates room if not listed
        Arguments:
            webex_token (cls): Api token for future requests
            webex_room (str): Name of webex room
            webex_email (str): Email to be added to the webex room
            webex_message (str): Str message to be sent
            webex_card (dict): Adaptive card for webex message
    """
    rooms = webex_token.rooms.list()
    aci_room = [room.id for room in rooms if room.title == webex_room]
    if aci_room:
        if webex_card:
            webex_token.messages.create(aci_room[0], text='\n',
                                        attachments=webex_card)
        else:
            webex_token.messages.create(aci_room[0], markdown=webex_message)
    else:
        webex_room = webex_token.rooms.create(webex_room)
        webex_token.memberships.create(webex_room.id, personEmail=webex_email)
        webex_token.messages.create(webex_room.id, text=webex_message)

def delete_webex_room(webex_token, webex_room):
    """
    Send a message to a supplied webex room
    Creates room if not listed
        Arguments:
            message (str): Str message to be sent
            webex_token (cls): Api token for future requests
            webex_room (str): Name of webex room
            webex_email (str): Email to be added to the webex room
    """
    rooms = webex_token.rooms.list()
    aci_room = [room.id for room in rooms if room.title == webex_room]
    if aci_room:
        webex_token.rooms.delete(aci_room[0])
        print(f"Sucessfully deleted {webex_room}")
    else:
        print(f"Webex room {webex_room}: Not Found")
