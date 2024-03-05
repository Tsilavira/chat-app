from pydantic import BaseModel, EmailStr

class UserLoginSchema(BaseModel):
    user_name: str
    password: str

class UserSchema(BaseModel):
    user_name: str
    email: EmailStr
    password: str

class LeaveGroupSchema(BaseModel):
    token: str
    group: str

class RemoveFriendGroupSchema(BaseModel):
    token: str
    group: str
    friend: str

class Msg(BaseModel):
    email: str
    date: str
    text: str

class WebSocketMessage(BaseModel):
    from_user: str
    to_user: str
    text: str
    date: str

class FriendFetch(BaseModel):
    token: str

class FriendQuery(BaseModel):
    token: str
    friend: str

class FriendPlus(BaseModel):
    token: str
    friend: str
    extra: str

class MessageFetch(BaseModel):
    token: str
    friend: str
    index: int

class FriendNotifs(BaseModel):
    token: str
    friend: str

class ResponseMessage:
    added_friend = ("succes", "Added friend.")
    removed_friend=  ("succes", "Removed friend.")
    group_exist = ("error", "Group alreadt exists.")
    group_set = ("succes", "Group set.")
    group_created = ("succes", "Group created.")
    user_not_in_group = ("error", "User is not in group.")
    added_to_group = ("succes", "Added to group.")
    invalid_details = ("error", "Invalid details were provided.")
    left_group = ("error", "Left the group.")
    is_read = ("succes", "Message read.")
    user_already_in_group = ("error", "User is already in group.")
    email_already_in_use = ("error", "This email is already used.")