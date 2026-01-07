import turtle
import time
import math
import random

ROAD_WIDTH = 20
ROAD_HALF_WIDTH = ROAD_WIDTH / 2

wn = turtle.Screen()
wn.title("Violka TD")
wn.bgcolor("black")
wn.setup(width=900, height=700)
wn.tracer(0)

# ==========================================
# PATH DRAWING
# ==========================================
path_drawer = turtle.Turtle()
path_drawer.hideturtle()
path_drawer.speed(0)
path_drawer.color("gray")
path_drawer.pensize(20)

waypoints = [
    (-350, 0),
    (-100, 0),
    (-100, 150),
    (150, 150),
    (150, -100),
    (350, -100),
]

path_drawer.penup()
path_drawer.goto(waypoints[0])
path_drawer.pendown()
for wp in waypoints[1:]:
    path_drawer.goto(wp)

# ==========================================
# UI LABELS
# ==========================================
sidebar = turtle.Turtle()
sidebar.hideturtle()
sidebar.penup()
sidebar.goto(340, 300)
sidebar.color("white")
sidebar.write("TOWERS", align="center", font=("Arial", 18, "bold"))

money_value = 20000
money_text = turtle.Turtle()
money_text.hideturtle()
money_text.penup()
money_text.goto(-350, -300)
money_text.color("white")

def update_money_display():
    money_text.clear()
    money_text.write(f"Money: {money_value}", font=("Arial", 18, "bold"))

update_money_display()

lives = 20
lives_text = turtle.Turtle()
lives_text.hideturtle()
lives_text.penup()
lives_text.goto(-50, -300)
lives_text.color("white")

def update_lives_display():
    lives_text.clear()
    lives_text.write(f"Lives: {lives}", font=("Arial", 18, "bold"))

update_lives_display()

# WAVE DISPLAY
wave_number = 1
wave_text = turtle.Turtle()
wave_text.hideturtle()
wave_text.penup()
wave_text.color("white")
wave_text.goto(150, -300)

def update_wave_display():
    wave_text.clear()
    wave_text.write(f"Wave: {wave_number}", font=("Arial", 18, "bold"))

update_wave_display()

# ==========================================
# GLOBAL LISTS
# ==========================================
towers = []
enemies = []
selected_tower_type = None
placing_mode = False

# ==========================================
# TOWER TYPES
# ==========================================
tower_types = {
    "Sniper": {"damage": 40, "range": 300, "speed": 1.5, "color": "purple", "cost": 150},
    "Splash": {"damage": 10, "range": 120, "speed": 1.0, "color": "orange", "cost": 140},
    "Fast":   {"damage": 40, "range": 150, "speed": 0.5, "color": "blue",   "cost": 100},
}

# ==========================================
# CREATE BUTTONS
# ==========================================
tower_buttons = []
button_y = 200

for t_type, props in tower_types.items():
    btn = turtle.Turtle()
    btn.shape("square")
    btn.color(props["color"])
    btn.shapesize(stretch_wid=2, stretch_len=2)
    btn.penup()
    btn.goto(340, button_y)
    tower_buttons.append((btn, t_type))

    label = turtle.Turtle()
    label.hideturtle()
    label.penup()
    label.color("white")
    label.goto(340, button_y + 20)
    label.write(f"{t_type} ({props['cost']})", align="center",
                font=("Arial", 10, "normal"))

    button_y -= 80


# ==========================================
# TOWER PLACEMENT CHECK (can't place on road)
# ==========================================
def point_to_segment_distance(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - x1, py - y1)
    t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
    t = max(0, min(1, t))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def is_on_road(x, y):
    for i in range(len(waypoints)-1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i+1]
        if point_to_segment_distance(x, y, x1, y1, x2, y2) <= ROAD_HALF_WIDTH + 5:
            return True
    return False


# ==========================================
# SELECT TOWER TYPE
# ==========================================
def select_tower(x, y):
    global selected_tower_type, placing_mode

    for btn, t_type in tower_buttons:
        if btn.distance(x, y) < 30:
            props = tower_types[t_type]
            if money_value < props["cost"]:
                print("Not enough money for", t_type)
                return
            selected_tower_type = t_type
            placing_mode = True
            print("Selected", t_type)

for btn, _ in tower_buttons:
    btn.onclick(select_tower)


# ==========================================
# PLACE TOWER ON MAP
# ==========================================
def place_tower(x, y):
    global placing_mode, selected_tower_type, money_value

    if not placing_mode:
        return
    if x > 280:
        return
    if is_on_road(x, y):
        print("Cannot place on road!")
        return

    props = tower_types[selected_tower_type]
    money_value -= props["cost"]
    update_money_display()

    towers.append(Tower(x, y, props["damage"], props["range"],
                        props["speed"], props["color"]))

    placing_mode = False
    selected_tower_type = None

wn.onclick(place_tower, btn=1)


# ==========================================
# TOWER CLASS
# ==========================================
class Tower:
    def __init__(self, x, y, damage, range_, speed, color):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_
        self.speed = speed
        self.cooldown = 0

        self.t = turtle.Turtle()
        self.t.shape("square")
        self.t.color(color)
        self.t.penup()
        self.t.goto(self.x, self.y)

        self.range_circle = turtle.Turtle()
        self.range_circle.hideturtle()
        self.range_circle.color("white")
        self.range_circle.pensize(2)
        self.range_circle.penup()

    def show_range(self):
        self.range_circle.clear()
        self.range_circle.goto(self.x, self.y - self.range)
        self.range_circle.pendown()
        self.range_circle.circle(self.range)
        self.range_circle.penup()
        self.range_circle.showturtle()

    def hide_range(self):
        self.range_circle.clear()
        self.range_circle.hideturtle()

    def was_clicked(self, x, y):
        return self.t.distance(x, y) < 20

    def update(self, dt, enemies):
        if self.cooldown > 0:
            self.cooldown -= dt
        for e in enemies:
            dist = math.hypot(e.x - self.x, e.y - self.y)
            if dist <= self.range and self.cooldown <= 0:
                e.health -= self.damage
                e.draw_health_bar()
                self.cooldown = self.speed
                break


# ==========================================
# ENEMY CLASS (Shortened)
# ==========================================
class Enemy:
    def __init__(self, x, y, type="Fast"):
        self.x = x
        self.y = y
        self.path_index = 0
        self.type = type

        if type == "Fast":
            self.max_health = 50
            self.health = 50
            self.speed = 120
            self.t = turtle.Turtle()
            self.t.color("yellow")
        elif type == "Tank":
            self.max_health = 300
            self.health = 300
            self.speed = 40
            self.t = turtle.Turtle()
            self.t.color("darkred")
        elif type == "Boss":
            self.max_health = 1500
            self.health = 1500
            self.speed = 50
            self.t = turtle.Turtle()
            self.t.shapesize(2)
            self.t.color("magenta")
        else:
            self.max_health = 100
            self.health = 100
            self.speed = 60
            self.t = turtle.Turtle()
            self.t.color("red")

        self.t.shape("circle")
        self.t.penup()
        self.t.goto(self.x, self.y)

        #self.t = turtle.Turtle()
        #self.t.shape("circle")
        #self.t.color(color)
        #self.t.penup()
        #self.t.goto(self.x, self.y)

        self.hp_bar = turtle.Turtle()
        self.hp_bar.hideturtle()
        self.hp_bar.penup()

    def draw_health_bar(self):
        w = 40
        h = 5
        x = self.x - w/2
        y = self.y + 20
        ratio = max(self.health, 0) / self.max_health
        
        self.hp_bar.clear()

        # red background
        self.hp_bar.goto(x, y)
        self.hp_bar.color("red")
        self.hp_bar.begin_fill()
        for _ in range(2):
            self.hp_bar.forward(w)
            self.hp_bar.left(90)
            self.hp_bar.forward(h)
            self.hp_bar.left(90)
        self.hp_bar.end_fill()

        # green foreground
        self.hp_bar.goto(x, y)
        self.hp_bar.color("green")
        self.hp_bar.begin_fill()
        for _ in range(2):
            self.hp_bar.forward(w * ratio)
            self.hp_bar.left(90)
            self.hp_bar.forward(h)
            self.hp_bar.left(90)
        self.hp_bar.end_fill()

    def move(self, dt):
        global lives

        if self.path_index >= len(waypoints)-1:
            self.t.hideturtle()
            self.hp_bar.clear()
            lives -= 1
            update_lives_display()
            return "escaped"

        tx, ty = waypoints[self.path_index+1]
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        step = self.speed * dt
        self.x += dx/dist * step
        self.y += dy/dist * step
        self.t.goto(self.x, self.y)

        self.draw_health_bar()

        if dist < step:
            self.path_index += 1

        return "alive"

    def is_dead(self):
        if self.health <= 0:
            self.t.hideturtle()
            self.hp_bar.clear()
            return True
        return False


# ==========================================
# CLICK TOWER TO SHOW RANGE (OPTION A)
# ==========================================
def handle_click(x, y):
    global placing_mode, selected_tower_type

    # Priority: placing a new tower
    if placing_mode:
        place_tower(x, y)
        return

    # Otherwise: check for tower selection
    clicked_any = False
    for t in towers:
        if t.was_clicked(x, y):
            # hide all other ranges
            for other_t in towers:
                other_t.hide_range()
            t.show_range()
            clicked_any = True
            break

    # clicked on empty area → hide all ranges
    if not clicked_any:
        for t in towers:
            t.hide_range()

wn.onclick(handle_click)

# ==========================================
# WAVE SYSTEM
# ==========================================
time_since_last_spawn = 0
spawn_delay = 1.0
enemies_to_spawn = 3
enemy_types_cycle = ["Fast","Tank","Boss"]

last_time = time.time()

# ==========================================
# MAIN GAME LOOP
# ==========================================
while True:
    if lives <= 0:
        print("GAME OVER")
        break

    now = time.time()
    dt = now - last_time
    last_time = now

    time_since_last_spawn += dt
    
    if enemies_to_spawn > 0 and time_since_last_spawn >= spawn_delay:
        e_type = enemy_types_cycle[(wave_number-1) % len(enemy_types_cycle)]
        enemies.append(Enemy(waypoints[0][0], waypoints[0][1], e_type))
        enemies_to_spawn -= 1
        time_since_last_spawn = 0

    if enemies_to_spawn == 0 and len(enemies) == 0:
        wave_number += 1
        enemies_to_spawn = 3 + wave_number * 2
        update_wave_display()

    # Move enemies
    new_list = []
    for e in enemies:
        if e.move(dt) != "escaped":
            new_list.append(e)
    enemies = new_list

    # Towers fire
    for t in towers:
        t.update(dt, enemies)

    # Kill dead enemies
    new_alive = []
    for e in enemies:
        if e.is_dead():
            money_value += 30
            update_money_display()
        else:
            new_alive.append(e)
    enemies = new_alive

    wn.update()
