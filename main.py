from fastapi import FastAPI, Request, WebSocket, Body, Depends, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

from decouple import config
import re
import bcrypt

from auth.jwt_handles import signJWT, decodeJWT
from auth.jwt_bearer import jwtBearer

import json

from function import *
from classes import *

salt = str(config("salt"))
bearer = jwtBearer(auto_Error=True)
app = FastAPI()
templates = Jinja2Templates(directory="build")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

response = ResponseMessage()

app.mount("/static", StaticFiles(directory="build/static"), name="static")






#signup endpoint
@app.post("/user/signup")
def user_signup(user: UserSchema = Body(default=None)):

    #chech for weird characters
    alphanumeric_regex = "^[a-zA-Z0-9]+$"
    if(bool(re.match(alphanumeric_regex, user.user_name)) and user.password.find(' ') == -1):

        if(check_user_already_used(user.user_name) == False):
            salt = bcrypt.gensalt()
            passhash = bcrypt.hashpw(user.password.encode('utf-8'), salt)

            add_user_to_database(user.user_name, user.email, passhash.decode("utf-8"), salt.decode('utf-8'))
            return signJWT(user.user_name)
        
        # return errors
        else:
            return response.email_already_in_use
    else:
        return response.invalid_details



#login endpoint
@app.post("/user/login")
def user_login(user: UserLoginSchema = Body(default=None)):
    #check if user exists before running a total match which costs a lot of computig  
    if check_user(user.user_name):

        #run a total check
        salt = get_salt(user.user_name)[0][0]
        if check_user_total(user.user_name, user.password, salt):
            return signJWT(user.user_name)
        
        #return errors
        else:
           return response.invalid_details
    else:
        return response.invalid_details
    


#get a list of friends endpoint
@app.post("/friend", dependencies=[Depends(bearer)])
def view_friends(f: FriendFetch):
    user = decodeJWT(f.token).get("userID")
    user_friends = check_friends(user)

    #chech is the user doesnt have any friends
    if user_friends[0][0] != None:

        #turn the bad data to a list
        friends_string = user_friends[0][0]
        friends_list = friends_string.split()   
        return friends_list
    
    #return no friends
    else:
        return []



#query friends from search bar endpoint
@app.post("/friendquery", dependencies=[Depends(bearer)])
def query_friend(f: FriendQuery):
    user = decodeJWT(f.token).get("userID")
    friend = f.friend

    #get users friends to not show the in the query list
    user_friends = check_friends(user)
    friends_string = user_friends[0][0]

    #return the query result
    response = query_friends(friends_string, user, friend)
    return response



#add friend endpoint
@app.post("/friendadd", dependencies=[Depends(bearer)])
def add_friend_end(f: FriendQuery):
    user = decodeJWT(f.token).get("userID")
    friend = f.friend

    #add friends while keeping the current friends
    friends = check_friends(user)
    return add_friend(friends, user, friend)



#remove friend endpoint
@app.post("/friendremove", dependencies=[Depends(bearer)])
def remove_friend(f: FriendQuery):
    user = decodeJWT(f.token).get("userID")
    friend = f.friend
    friends = check_friends(user)

    #make new friends list out of old one
    list  = friends[0][0].split()
    removed_list = [n for n in list if n != friend]
    result = ' '.join(removed_list)

    #set the friend list in database
    return set_friends(result, user)



#get groups endpoint
@app.post("/getgroups", dependencies=[Depends(bearer)]) 
def get_groups(user: FriendFetch):
    user = decodeJWT(user.token).get("userID")
    list = check_groups(user)

    #chech if user isnt in any groups
    if list[0][0] != None:    
        list_sting = list[0][0]
        grous_list = list_sting.split()   
    else:
        grous_list = []
    return grous_list



#create group endpoint
@app.post("/creategroup", dependencies=[Depends(bearer)]) 
def get_groups(user: FriendQuery):
    userr = decodeJWT(user.token).get("userID")
    group_name = user.friend
    group_exists = group_exist(group_name)

    #check if group exists
    if group_exists:
        return response.group_exist
    else: 

        #check if user is in groups
        b = check_groups(userr)
        if b == [(None,)]: # nog geen group
            set_group(group_name, userr)

        #weird string manipulation for database
        else:
            b = b[0]
            value = b[0].strip() if isinstance(b[0], str) else None
            b = value + " " + group_name
            set_group(b, userr)
        
        #set group in database
        insert_group(group_name, userr)
        return response.group_created



#add user to group endpoint
@app.post("/addtogroup", dependencies=[Depends(bearer)])
def get_groups(temp: FriendPlus):
    user = decodeJWT(temp.token).get("userID")
    friend = temp.friend
    group = temp.extra
    is_in_group = False

    #check if the requesting user is in the group
    user_groups = check_groups(user)
    groups = user_groups[0][0].split()
    for n in groups:
        if n == group:
            is_in_group = True

    #chech if the friend isnt already in group
    friend_groups = check_groups(friend)
    goops = friend_groups[0][0].split()
    for n in goops:
        if n == group:
            return response.user_already_in_group

    #a bunch of checks to see if the user already has groups to properly format the database input
    if is_in_group:
        b = check_groups(friend)
        if (b[0] == (None,)): #no groups yet
            insert = " "+ group
            set_group(insert, friend)
        elif b[0][0] == group:
            return response.user_already_in_group
        else:
            b = b[0]
            value = b[0].strip() if isinstance(b[0], str) else None
            insert = value + " " + group
            set_group(insert, friend)

        c = get_group_members(group)
        new_memb_list = c[0][0] + " " + friend
        set_members(new_memb_list, group)
        
        d = check_groups(friend)
        if d == [(None,)]: # nog geen group
            set_group(group, friend)
        else:
            d = d[0]
            value = d[0].strip() if isinstance(d[0], str) else None
            inset = value + " " + group
            set_group(inset, friend)

    #returns
        return response.added_to_group
    else:
        return response.user_not_in_group



#remove a friend from a group endpoint
@app.post("/removefriendfromgroup", dependencies=[Depends(bearer)])
def get_groups(user: RemoveFriendGroupSchema):
    name = decodeJWT(user.token).get("userID")
    friend = user.friend
    group = user.group

   #check if the requesting user is in the group
    user_groups = check_groups(name)
    groups = user_groups[0][0].split()
    for n in groups:
        if n == group:
            is_in_group = True

    if is_in_group:
        #get group members
        members = get_group_members(group)
        members_list = members[0][0].split()
        members_list.remove(friend)

        set_members(convert_list_to_database_list(members_list), group)

        groups = check_groups(friend)
        groups_list = groups[0][0].split()
        groups_list.remove(group)

        #new group list data
        if (len(groups_list) < 1):
            set_group(None, friend)
        else: 
            string = ""
            i = 0
            while i < len(groups_list):
                string += " "
                string += groups_list[i]
                i+=1
            set_group(string, friend)

        return response.removed_friend
    else:
        return response.user_not_in_group



#leave a group endpoint (remove yourself)
@app.post("/leavegroup", dependencies=[Depends(bearer)])
def get_groups(user: LeaveGroupSchema):
    username = decodeJWT(user.token).get("userID")
    group = user.group

    #create a new member list where user is removed
    members = get_group_members(group)
    members_list = members[0][0].split()
    members_list.remove(username)

    #set the new list, while converting list
    set_members(convert_list_to_database_list(members_list), group)

    #remove the group from the users group list
    groups = check_groups(username)
    groups_list = groups[0][0].split()
    groups_list.remove(group)

    #chech if the user has 0 groups left and handle it
    if (len(groups_list) < 1):
        set_group(None, username)
    else: 
        string = ""
        i = 0
        while i < len(groups_list):
            string += " "
            string += groups_list[i]
            i+=1
        set_group(string, username)

    return response.left_group



#get the lift of members in aa group endpoint
@app.post("/getmember", dependencies=[Depends(bearer)])
def get_mem(group: FriendQuery):
    user = decodeJWT(group.token).get("userID")
    group_name = group.friend

    #get the members and turn it into a list
    members = get_group_members(group_name)
    members_list = members[0][0].split()

    #if the requesting user is in the list, return it
    if (user in members_list):
        return members_list
    else:
        return response.user_not_in_group




#get messages in a chat endpoint
@app.post("/getmessage", dependencies=[Depends(bearer)])
def get_mem(msg: MessageFetch):
    MESSAGESPERTIME = 20 #this is the amount of messages to fetch per session
    user = decodeJWT(msg.token).get("userID")
    friend = msg.friend
    index = msg.index

    #get the messages and set them as read
    messages = get_messages(user, friend, index, MESSAGESPERTIME)
    set_read(user, friend, index, MESSAGESPERTIME)
    return messages



#get notifications of user 
#this is currently useless, but might come in handy
@app.post("/getnotifs", dependencies=[Depends(bearer)])
def get_mem(request: FriendNotifs):
    user = decodeJWT(request.token).get("userID")
    friend = request.friend
    notifs = get_notifs(user, friend)
    return notifs



#ws_conns and group_list for caching
ws_conns = []
group_list = []

#websocket endpoint
@app.websocket("/ws/{token}")
async def websocket_connection(ws: WebSocket, token:str):
    await ws.accept()
    user_name = ""

    #check if the token is valid
    if (decodeJWT(token) != None):
        user_name = decodeJWT(token)["userID"]

        #cache the groups and the members
        group_array = check_groups(user_name)[0][0].split()
        for n in group_array:
            if n not in [item[0] for item in group_list]:
                members = get_group_members(n)[0][0].split()
                group_list.append((n, members))
                
        #append the users and its connection
        ws_conns.append((user_name, ws))

    #raise errors
    else:
        raise WebSocketDisconnect

    #check for messages
    try:
        while True:

            #save the message to database
            data = await ws.receive_text() 
            json_data = WebSocketMessage(**json.loads(data))
            json_data.from_user = decodeJWT(json_data.from_user)['userID']
            save_message_to_database(json_data)

            #handle group messages
            if json_data.to_user[:2] == 'g:':
                group_name = json_data.to_user[2:]

                #make an array where the sender is removed
                split_cheese = get_group_members(group_name)[0][0].split()
                if json_data.from_user in split_cheese:
                    split_cheese.remove(json_data.from_user)

                #try to message each online person of the group array
                for j in split_cheese:
                    for i in ws_conns:
                        if j == i[0]:
                            live_comm_message = {"user" : json_data.from_user, 
                                "text" : json_data.text,
                                "date" : json_data.date,
                                "chat" : json_data.to_user}
                            await i[1].send_text(json.dumps(live_comm_message))
                            
            #send a ws message to the designated user              
            for tup in ws_conns:
                if tup[0] == json_data.to_user:
                    live_comm_message = {"user" : json_data.from_user, 
                                        "text" : json_data.text,
                                        "date" : json_data.date,
                                        "chat" : json_data.to_user}
                    await tup[1].send_text(json.dumps(live_comm_message))

            #return a message to the sender
            return_message = {"user" : json_data.from_user, 
                              "text" : json_data.text,
                              "date" : json_data.date,
                              "chat" : json_data.to_user}
            await ws.send_text(json.dumps(return_message))

    #handle disconnect
    except WebSocketDisconnect:
        ws_conns.remove((user_name, ws))



@app.get("/{path:path}", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})