import droneutil as du
#import alprutil as au
import imgutil as iu

drone = du.get_drone()
# drone = du.get_drone(videoOn=False)
#alpr = au.get_alpr()


def manual_flight():
    du.manual_control(drone)

'''
def lp_surveillance():
    folder_name = 'license plate - ' + du.current_time_str()

    def detect_lp():
        img_path = du.save_img(drone, folder_name)
        plates = au.detect_plates(alpr, img_path)
        if plates is not None:
            au.print_plates(plates)

    du.manual_control(drone, func=detect_lp)

'''
def follow_color_blob():
    
    print('gog')
    #minhsv, maxhsv = iu.get_range(drone.frame)
    minhsv, maxhsv = (154, 111, 0), (255, 255, 255) # hsv for orange ping-pong ball
    du.follow(drone, minhsv, maxhsv, False)

follow_color_blob()
