import pyardrone as ps_drone
import cv2
import imgutil

import os
import time


OPTIMAL_MVSPEED = 0.2 #0.25
OPTIMAL_LTURN_SPEED = 0.5
OPTIMAL_RTURN_SPEED = 0.65
OPTIMAL_UPDOWN_SPEED = 0.1 #0.4


def print_battery(drone):
    drone.printBlue('Battery: ' + str(drone.getBattery()[0]) +
                    '% ' + str(drone.getBattery()[1]))


def save_img(drone, folder_name):
    cv2img = drone.frame

    root_path = '/home/guyu/py/ps_drone/camera_img/'
    if not os.path.isdir(root_path + folder_name):
        os.makedirs(root_path + folder_name)

    img_path = '%s%s/drone_%d.jpg' % (root_path, folder_name, 12)

    cv2.imwrite(img_path, cv2img)
    return img_path


def get_drone(defaultSpeed=OPTIMAL_MVSPEED, videoOn=True):
    drone = ps_drone.ARDrone()
    '''
    # Wait till the drone fully resets
    time.sleep(2)

    # getBattery() returns (batValue percent), batStatus(OK or empty))
    while drone.getBattery()[0] == -1:
        time.sleep(0.1)

    # Give the drone some time to fully awake
    time.sleep(0.5)'''

    # "demo", "vision detect" and "chksum" packages of Navdata
    # are available 15 times per second
    #drone.useDemoMode(True)
    '''
    # Recalibrate sensors
    drone.trim()
    drone.mtrim()

    # Set the speed of the drone
    drone.setSpeed(defaultSpeed)

    print_battery(drone)
    '''
    # Initialize the drone's video function
    if videoOn:
        drone.video_ready.wait()

    return drone


def do(func, duration):
    if func is None:
        time.sleep(duration)
        return

    t = time.time()
    while time.time() - t < duration:
        func()
        time.sleep(0.01)


def current_time_str():
    def two_digit(digits):
        if len(digits) == 1:
            return '0' + digits
        return digits

    t = time.gmtime()
    timestr = ''
    for i in range(6):
        s = str(t[i])
        if len(s) == 1:
            s = '0' + s
        if i < 2:
            s += '-'
        elif i == 2:
            s += ' '
        elif i < 5:
            s += ':'

        timestr += s

    return timestr


control_message = \
    """

    ---CONTROL MANUAL---
    SPACE:  LAND/TAKE OFF
    W:      MOVE FOWARD
    S:      MOVE BACKWARD
    A:      MOVE LEFT
    D:      MOVE RIGHT
    Q:      TURN LEFT
    E:      TURN RIGHT
    P:      TAKE PICTURE
    U:      MOVE UP
    I:      MOVE DOWN
    N:      TERMINATE CONTROL
    H:      SHOW MANUAL

    """


controls_dict = {
    ' ': 'Taking off/Landing...',
    'w': 'Moving forward...',
    's': 'Moving backward...',
    'a': 'Movin left...',
    'd': 'Moving right...',
    'q': 'Turning left...',
    'e': 'Turning right...',
    'p': 'Taking a picture...',
    'u': 'Moving up...',
    'i': 'Moving down...',
    'n': 'Terminating control...',
    'h': control_message
}


def manual_control(drone, interval=1, func=None):
    stop = False
    session_time = current_time_str()
    drone.printBlue(control_message)

    while not stop:
        key = drone.getKey()

        # Check if key is valid
        if key in controls_dict:
            drone.printBlue(controls_dict[key])
        elif key != '':
            drone.printRed('"%s" is an invalid command.' % key)
            continue

        # Press space to toggle landing / taking off
        if key == ' ':
            is_landed = drone.state[0][2]
            is_flying = drone.NavData[0][3]
            if is_landed and not is_flying:
                drone.takeoff()
                time.sleep(4)
            else:
                drone.land()
                time.sleep(4)

        # L to take picture
        elif key == 'p':
            img_path = save_img(drone, session_time)
            drone.printGreen('Picture stored in %s' % img_path)

        # N to terminate control
        elif key == 'n':
            drone.land()
            time.sleep(4)
            stop = True

        # It received movement commands:
        # func is only executed during these commands
        else:
            # WASD for moving
            if key == 'w':
                drone.move(forward=OPTIMAL_MVSPEED)
            elif key == 's':
                drone.move(backward=OPTIMAL_MVSPEED)
            elif key == 'a':
                drone.move(left=OPTIMAL_MVSPEED)
            elif key == 'd':
                drone.move(right=OPTIMAL_MVSPEED)

            # QE for turning
            elif key == 'q':
                drone.move(cw=OPTIMAL_LTURN_SPEED)
            elif key == 'e':
                drone.move(ccw=OPTIMAL_RTURN_SPEED)

            # UI for going up/down
            elif key == 'u':
                drone.move(up=OPTIMAL_UPDOWN_SPEED)
            elif key == 'i':
                drone.move(down=OPTIMAL_UPDOWN_SPEED)

            # Execute the function, and stop the drone
            do(func, interval)
            drone.hover()
            time.sleep(1)

        # Command successful
        if key != '':
            drone.printGreen('Command Successful.')


def follow(drone, minhsv, maxhsv, testing=False):
    
    if not testing:
        # Try taking off
        is_landed = True#drone.state[2]
        is_flying = False#drone.state[3]
        if is_landed and not is_flying:
            drone.takeoff()

        else:
            print("Mike")
    
    x_error = 640 / 10
    y_error = 360 / 10
    cx = 640 / 2
    cy = 360 / 2
    speed = 1
    def percent_diff(img1,img2):
        top=abs(img1-img2)
        bot=(img1+img2)/2
        ans=top/bot
        return ans*1

    def normalize(loc, center, error):
        dist = center - loc
        pos=percent_diff(center,loc)
        if abs(dist) < error:
            return 0
        if dist < 0:
            return -pos
        return pos

    stop = False
    while not stop:
        key = None#drone.getKey()
        if key == ' ':
            stop = True
            drone.land()
        else:
           # location detection method here
            location = imgutil.get_center(drone.frame, minhsv, maxhsv)
            if not location:
                drone.hover()
                continue
            x, y = location[1]
            vx = normalize(x, cx, x_error) * speed * -1
            vy = normalize(y, cy, y_error) * speed
            # right, forward, up, turn
            if not testing:
                drone.move(right=vx,forward=0,up=vy,cw=0)
            # else:
            print('speed_x: ', vx, 'speed_y: ', vy)

            time.sleep(0.1)
