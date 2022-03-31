import pygame as pg
from math import sqrt
from random import randint
from os import system, name
from time import time as get_time
import sqlite3

class window_class:
    def __init__(self, width, height):
        self.display, self.height, self.width = pg.display.set_mode((width, height)), height, width

class target_class:
    def __init__(self, pos, radius):
        self.pos, self.radius = pos, radius
    def draw(self, display, dist_to_mouse):
        pg.draw.circle(display, ([255-(dist_to_mouse%255),50,dist_to_mouse%255]), (self.pos[0],self.pos[1]), self.radius, 0)

class mouse_class:
    def __init__(self, radius):
        self.radius, self.pos = radius, pg.mouse.get_pos()
    def update_pos(self):
        self.pos = pg.mouse.get_pos()
    def draw(self, display):
        self.update_pos()
        pg.draw.circle(display, (130,150,25), (self.pos[0],self.pos[1]), self.radius, 0)

def update_pg_display(window, mouse, target_bank):
    window.display.fill((255, 255, 225))
    for i in range(len(target_bank)-1,-1,-1):
        target = target_bank[i]
        dist_to_mouse = min(int(sqrt(((target.pos[0]-mouse.pos[0])**2) + ((target.pos[1]-mouse.pos[1])**2))), 254)
        #print(dist_to_mouse)
        if dist_to_mouse < target.radius+mouse.radius:
            target_bank.pop(i)
        else:
            target.draw(window.display, dist_to_mouse)

    mouse.draw(window.display)
    pg.display.flip() # Updates the window

def main():
    window = window_class(600,400)
    mouse = mouse_class(10)
    target_bank, targets = [], 6
    for i in range(targets):
        target_bank.append(target_class([randint(5,window.width-5),randint(5,window.height-5)], 8))
    running = True
    start_time = get_time()
    while running:
        mouse.update_pos()
        update_pg_display(window, mouse, target_bank)
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONUP:
                pass
        #print(len(target_bank))
        if len(target_bank) == 0:
            time = round(get_time()-start_time, 3)
            print("You won in ", time, "seconds")
            pg.quit()
            running = False
    username = ""
    while len(username) == 0:
        username = input("Enter your username: ")

    conn = sqlite3.connect("leaderboard.db")
    table_name = "tblLeaderboard"
    #print("create_leaderboard")
    create_leaderboard(conn.cursor(), table_name)
    
    #print("get_rec")
    rec_exists, user_data = get_rec(conn.cursor(), table_name, username)
    if rec_exists:
        if time < user_data[1]:
            print("Congrats! You beat your previous fastest time by", (user_data[1]-time))
            update_rec(conn, username, time, table_name)
        else:
            print("Your time was", time, "but your fastest time is", user_data[1])
    else:
        #print("add_rec")
        add_rec(conn, username, time, table_name)
    print("Current Leaderboard:")
    get_leaderboard(conn.cursor(), table_name)
    

def create_leaderboard(cursor, table_name):
    try:
        cursor.execute(f"CREATE TABLE {table_name} (userName TEXT, time FLOAT, PRIMARY KEY (userName))")
    except:
        pass
        #print("Database table already exists")

def add_rec(conn, username, time, table_name):
    try:
        conn.cursor().execute(f"""INSERT INTO {table_name} VALUES (?, ?)""", (username,time))
        conn.commit()
        print("record added for", username)
    except sqlite3.Error as e:
        print(e)

def get_rec(cursor, table_name, username):
    username = "\""+username+"\""
    cursor.execute(f"""SELECT * FROM {table_name} WHERE userName = {username}""")
    row = cursor.fetchone()
    try:
        user_data = [row[0], float(row[1])]
        return True, user_data
    except:
        return False, row

def update_rec(conn, username, time, table_name):
    try:
        conn.cursor().execute(f"""UPDATE {table_name} SET time = {time} WHERE userName = {username}""")
        conn.commit()
        print("record updated for", username)
    except sqlite3.Error as e:
        print(e)

def get_leaderboard(cursor, table_name):
    curr_pos = 1
    for row in cursor.execute(f"SELECT * FROM {table_name} ORDER BY time LIMIT 10"):
        print(curr_pos, "-", row[0], "with a time of", row[1], "secs")
        curr_pos += 1

if __name__ == '__main__':
    main()
