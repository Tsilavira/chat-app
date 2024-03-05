import sqlite3 
from classes import *
import bcrypt

response = ResponseMessage()

#Saves message to database
def save_message_to_database(msg: WebSocketMessage):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Messages (from_user, to_user, text_data, date_data) VALUES (?, ?, ?, ?)", (msg.from_user, msg.to_user, msg.text, msg.date))
    conn.commit()
    conn.close()

#Adds user to database
def add_user_to_database(username, email, password, salt):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (username, email, password, salt) VALUES (?, ?, ?, ?)", (username, email, password, salt))
    cursor.execute("INSERT INTO Friends (user) VALUES (?)", (username,))
    conn.commit()
    conn.close()

def get_salt(user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT salt FROM Users WHERE username = ?", (user,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    return u

#Check if email and password match
def check_user(user_name):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users WHERE username = ?", (user_name,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(u) == 1:
        return True
    return False

def check_user_total(username, password, salt):
    salt_byte = salt.encode("utf-8")
    pass_hash = bcrypt.hashpw(password.encode('utf-8'), salt_byte)
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM Users WHERE username = ?", (username,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    if u[0][0] == pass_hash.decode('utf-8'):
        return True
    else: 
        return False


#Check if the email is already used by someone
def check_email_already_used(email): 
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users where email = ?", (email,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(u) == 1:
        return True
    return False

#Check if the username is already used by someone
def check_user_already_used(user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ?", (user,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(u) == 1:
        return True
    return False

#check who friends are
def check_friends(user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT friends from FRIENDS where user = ?", (user,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    return u

#does not include user self
def query_friends(friends_string, user, friend):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    if(friends_string == None):
        friends_string = ""
        query = f"""
        SELECT username
        FROM Users
        WHERE username LIKE '%' || ? || '%'
        AND username != ?
        """
        params = [friend, user]
    else:
        friends_list = friends_string.split()
        placeholders = ",".join(["?" for _ in friends_list])
        query = f"""
        SELECT username
        FROM Users
        WHERE username LIKE '%' || ? || '%'
        AND username != ?
        AND username NOT IN ({placeholders})
        """
        params = [friend, user] + friends_list
    cursor.execute(query, params)
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    return u

#adds firend, also checks for existing friends
def add_friend(old_friends, user, new_friend):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    if(old_friends[0] == (None,)): #first friend
        old_friends = " "+ new_friend
        set_friends(old_friends, user)
        return response.added_friend
    else: #already has friends
        old_friends = old_friends[0]
        value = old_friends[0].strip() if isinstance(old_friends[0], str) else None
        old_friends = value + " " + new_friend
        set_friends(old_friends, user)
        return response.added_friend

#set friend value
def set_friends(friends, user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE friends SET friends = ? WHERE user = ?', (friends, user)) 
    conn.commit()
    conn.close()
    return response.removed_friend

#get users groups
def check_groups(user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT groups from USERS where username = ?", (user,))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    return u

#check if the group exists
def group_exist(group):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Groups where name = ?", (group,))
    a = cursor.fetchall()
    conn.commit()
    conn.close()
    if len(a) > 0:
        return True
    else:
        return False
    
#set group to username
def set_group(group, user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET groups = ? WHERE username = ?", (group, user))
    conn.commit()
    conn.close()
    return response.group_set

#insert user-group pair into the group
def insert_group(group, user):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Groups (members, name) VALUES (?, ?)", (user, group))
    conn.commit()
    conn.close()

#get group members of goup
def get_group_members(group):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT members FROM groups WHERE name = ?", (group,))
    u = cursor.fetchall();
    conn.commit()
    conn.close()
    return u

def set_members(members, group):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE groups SET members = ? WHERE name = ?", (members, group))

    conn.commit()
    conn.close()

def convert_list_to_database_list(array):
    stringcheese = ""
    j = 0
    while j < len(array):
        stringcheese += " "
        stringcheese += array[j]
        j+=1
    return stringcheese

def get_message_(user, friend, index: int):
    conn = sqlite3.connect('database/main.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text_data FROM Messages WHERE from_user = ? AND to_user = ? LIMIT 10 OFFSET ?", (user, friend, index))
    u = cursor.fetchall()
    conn.commit()
    conn.close()
    return u

def get_messages(from_user, to_user, index, length):
    conn = sqlite3.connect('database/main.db')   
    cursor = conn.cursor()
    #handle groups
    if to_user[:2] == "g:":
        if index == 0:
            cursor.execute(
                """
                SELECT text_data, from_user, date_data
                FROM messages
                WHERE to_user = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (to_user, length)
            )
        else:
            cursor.execute(
                """
                SELECT text_data, from_user, date_data
                FROM messages
                WHERE to_user = ? AND id IN (
                    SELECT id
                    FROM messages
                    WHERE to_user = ?
                    ORDER BY id DESC
                    LIMIT ?
                    OFFSET ?
                )
                ORDER BY id DESC
                """,
                (to_user, to_user, length, index)
            )
    #handle normal users
    else:
        if index == 0:
            cursor.execute(
                """
                SELECT text_data, from_user, date_data
                FROM messages
                WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
                ORDER BY id DESC
                LIMIT ?
                """,
                (from_user, to_user, to_user, from_user, length)
            )
        else:
            cursor.execute(
                """
                SELECT text_data, from_user, date_data
                FROM messages
                WHERE ((from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)) AND id IN (
                    SELECT id
                    FROM messages
                    WHERE (from_user = ? AND to_user = ?) OR (from_user = ? AND to_user = ?)
                    ORDER BY id DESC
                    LIMIT ?
                    OFFSET ?
                )
                ORDER BY id DESC
                """,
                (from_user, to_user, to_user, from_user, from_user, to_user, to_user, from_user,length, index)
            )
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    array = []
    count = 0
    for n in messages:
        array.append({"user" : n[1], "text" : n[0],"date" : n[2]})  
        count = count + 1
    return array

def set_read(from_user, to_user, index, length):
    conn = sqlite3.connect('database/main.db')   
    cursor = conn.cursor()
    if index == 0:
        cursor.execute(
            """
            UPDATE Messages
            SET is_read = 1
            WHERE from_user = ?
            AND to_user = ?
            AND id IN (SELECT id FROM Messages WHERE from_user = ? AND to_user = ? ORDER BY id DESC LIMIT ?);
            """,
            (from_user, to_user, from_user, to_user, length)
        )
    else:
       cursor.execute(
            """
            UPDATE messages
            SET is_read = 1
            WHERE from_user = ? 
            AND to_user = ? 
            AND id IN (
                SELECT id
                FROM messages
                WHERE from_user = ? 
                AND to_user = ?
                ORDER BY id DESC
                LIMIT ?
                OFFSET ?
            );
            """,
            (from_user, to_user, from_user, to_user, length, index)
        )
    cursor.close()
    conn.close()
    return response.is_read


def get_notifs(user, friend):
    conn = sqlite3.connect('database/main.db')   
    cursor = conn.cursor()

    cursor.execute(
    """
    SELECT COUNT(*)
    FROM messages
    WHERE from_user = ? AND to_user = ? AND is_read IS NULL;
    """, 
    (user, friend)
    )

    notifs = cursor.fetchall()
    cursor.close()
    conn.close()
    return notifs[0][0]
