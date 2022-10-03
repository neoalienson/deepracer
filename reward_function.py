import math

def reward_function(params, verbose=True):
    global VERBOSE
    global DEBUG
    global reward
    global distance_reward
    global speed_reward
    global all_wheels_on_track
    global x
    global y
    global DISTANCE_FROM_CENTER
    global is_left_of_center
    global heading
    global progress
    global steps
    global speed
    global steering_angle
    global TRACK_WIDTH
    global waypoints
    global closest_waypoints
    global is_offtrack

    ABS_STEERING_THRESHOLD = 5
    
    # first 45 iteration
    STAGE = 2
    
    if STAGE == 1:
      DISTANCE_MULTIPLIER = 1
      STEERING_MULTIPLIER = 0
      SPEED_MULTIPLIER    = 0
      PROGRESS_MULTIPLIER = 0.5

    if STAGE == 2:
      DISTANCE_MULTIPLIER = 1
      STEERING_MULTIPLIER = 0
      SPEED_MULTIPLIER    = 1
      PROGRESS_MULTIPLIER = 0.5

    setup(verbose)
    read_params(params)
    #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
    racing_track = [
            [2.8996075272629778, 0.6341873042211996],
            [3.171790692640738, 0.6146661404686171],
            [3.4152074832399077, 0.6051347353884229],
            [3.669338799363328, 0.6005152465249329],
            [4.189995119968753, 0.6],
            [4.429130766541965, 0.6009732953143176],
            [4.676006572225383, 0.603104085669501],
            [5.090065986401652, 0.6117211573948813],
            [5.476498526979427, 0.635850915161187],
            [5.7823607773066765, 0.675259134935313],
            [6.027544536849749, 0.7295097948543414],
            [6.237703144489084, 0.7952207246735367],
            [6.420400141319679, 0.872024037973577],
            [6.580332753839865, 0.9599125080900942],
            [6.7190515476869805, 1.0599771428214355],
            [6.836302755078611, 1.1741375056741075],
            [6.929726303183032, 1.305019919854189],
            [6.995719844809193, 1.4537764515420886],
            [7.0365925223431365, 1.6157745267826396],
            [7.044624347983953, 1.7898733812431518],
            [7.007905544629744, 1.9702698012962891],
            [6.9278734051849025, 2.1472855013902943],
            [6.7905576371312835, 2.3057833266025245],
            [6.6169615677555464, 2.440933911531645],
            [6.417890652611375, 2.5500959775940863],
            [6.203926405011183, 2.636045215166738],
            [5.982147310504509, 2.704128828597474],
            [5.7567003844686955, 2.7605989607780406],
            [5.551452256378178, 2.8057811212455332],
            [5.348950049032069, 2.8575505210350496],
            [5.149506355250921, 2.917487669937737],
            [4.953316665510342, 2.987358119593436],
            [4.760750562273259, 3.070518913395613],
            [4.572153138902202, 3.1728119064952347],
            [4.386270961468906, 3.2908544596106593],
            [4.202454093237401, 3.4208241454478],
            [4.0201158703996835, 3.55894483807861],
            [3.838559410803195, 3.701238063190881],
            [3.6855691118899454, 3.818362600086325],
            [3.5318614056087005, 3.9298082568136516],
            [3.376767170587105, 4.0327542801356095],
            [3.2193053241371072, 4.12479025215649],
            [3.0581790077500983, 4.204201585861126],
            [2.891920986902783, 4.270149824437261],
            [2.719032851018891, 4.322362824415513],
            [2.5382985584669786, 4.361122649342377],
            [2.3481271748808576, 4.385796538227344],
            [2.1456978405598743, 4.393725364373829],
            [1.9273248958290683, 4.380325143281793],
            [1.6868242856643292, 4.334246593248443],
            [1.4230477940641797, 4.234830794928121],
            [1.160770132150102, 4.058322509520716],
            [0.9505947324234407, 3.7847005373669402],
            [0.857103182859364, 3.4171386887429427],
            [0.8486331414700211, 3.056289779740127],
            [0.8784022340973037, 2.7781960164655075],
            [0.913357386730385, 2.5656455721475884],
            [0.9632225282184916, 2.308769099616856],
            [1.011127093080785, 2.100019969703246],
            [1.0673191409828982, 1.8986347005434878],
            [1.1342245359295289, 1.705581668112396],
            [1.2130937946005345, 1.525207621090658],
            [1.304471621070306, 1.361113005046645],
            [1.4094428418298646, 1.2150711746249088],
            [1.5308995618061925, 1.0873769135326024],
            [1.6795165697820584, 0.978799956737326],
            [1.856588325684347, 0.8824571252158953],
            [2.067494915089296, 0.7974296405926341],
            [2.3183633689595777, 0.7254717201119107],
            [2.604489994025146, 0.6701721836295073],
            [2.8996075272629778, 0.6341873042211996]]


    # Get closest indexes for racing line (and distances to all points on racing line)
    closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

    # Get optimal [x, y, speed, time] for closest and second closest index
    optimals = racing_track[closest_index]
    optimals_second = racing_track[second_closest_index]

    reward = 0.001

    ## Reward if car goes close to optimal racing line ##
    dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
    distance_reward = max(1e-3, 1 - (dist/(TRACK_WIDTH*0.5)))
    reward += distance_reward * DISTANCE_MULTIPLIER
 
    # reward if steer less
    if abs(steering_angle) < ABS_STEERING_THRESHOLD:
        reward += 0.2 * STEERING_MULTIPLIER
   
    speed_reward = params["speed"] / 8
    reward += speed_reward * SPEED_MULTIPLIER

    # progress reward
    progress_reward = PROGRESS_MULTIPLIER
    reward += progress_reward

    if all_wheels_on_track == False:
        reward = 0.001

    # Zero reward if obviously wrong direction (e.g. spin)
    direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
    if direction_diff > 30:
        reward = 0.001
        if verbose:
            print(f"WRONG DIRECTION: {direction_diff:.1f}")

    print_params()

    return float(reward)

def setup(verbose):
    global VERBOSE
    global DEBUG
    VERBOSE = verbose
    DEBUG = False

def print_params():
    global VERBOSE
    global DEBUG
    global reward
    global distance_reward
    global speed_reward
    global all_wheels_on_track
    global x
    global y
    global DISTANCE_FROM_CENTER
    global is_left_of_center
    global heading
    global progress
    global steps
    global speed
    global steering_angle
    global TRACK_WIDTH
    global waypoints
    global closest_waypoints
    global is_offtrack

    if not VERBOSE:
        return    
    import math
    print(f"r:{reward:.2f} {'*' * math.ceil(reward*5)}{' ' * math.floor(20-reward*5)}", end =" ")
    print(f"sr:{speed_reward:.1f} {'*' * math.ceil(speed_reward*2.5)}{' ' * math.floor(10-speed_reward*2.5)}", end =" ")
    print(f"dr:{distance_reward:.1f} {'*' * math.ceil(distance_reward*10)}{' ' * math.floor(10-distance_reward*10)}", end =" ")
    speed_bar = (speed - 1.3) * 10.0 / (4.0 - 1.3)            
    print(f'sp: {speed:.1f} {"=" * math.ceil(speed_bar)}{" " * math.floor(10 - speed_bar)}', end = ' ')
    _l = max(0, steering_angle / 3)
    print(f'sa: {steering_angle:5.1f} {" " * math.floor(10 - _l)}{"<" * math.ceil(_l)}', end = '|')
    _r = max(0, steering_angle / -3)
    print(f'{">" * math.ceil(_r)}{" " * math.floor(10 - _r)}', end = ' ')
    print(f'x: {x:.1f}, y: {y:.1f}, h: {heading:.1f}')
    if DEBUG == True:
        print(f'dc: {DISTANCE_FROM_CENTER:.2f}, p: {progress:.2f}, st: {steps:3.0f}, cw: {closest_waypoints}, 1c: {closest_index}, 2c: {second_closest_index}, aw: {all_wheels_on_track}, il: {is_left_of_center}, ')
        print(f'ot: {is_offtrack}, tw: {TRACK_WIDTH:.2f}')

def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):    
        # Calculate the distances between 2 closest racing points
        a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

        # Distances between car and closest and second closest racing point
        b = abs(dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1]))
        c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

        # Calculate distance between car and racing line (goes through 2 closest racing points)
        # try-except in case a=0 (rare bug in DeepRacer)
        try:
            distance = abs(-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                           (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
        except:
            distance = b

        return distance

def dist_2_points(x1, x2, y1, y2):
            return abs(abs(x1-x2)**2 + abs(y1-y2)**2)**0.5

def closest_2_racing_points_index(racing_coords, car_coords):

            # Calculate all distances to racing points
            distances = []
            for i in range(len(racing_coords)):
                distance = dist_2_points(x1=racing_coords[i][0], x2=car_coords[0],
                                         y1=racing_coords[i][1], y2=car_coords[1])
                distances.append(distance)

            # Get index of the closest racing point
            closest_index = distances.index(min(distances))

            # Get index of the second closest racing point
            distances_no_closest = distances.copy()
            distances_no_closest[closest_index] = 999
            second_closest_index = distances_no_closest.index(
                min(distances_no_closest))

            return [closest_index, second_closest_index]

        # Calculate which one of the closest racing points is the next one and which one the previous one
def next_prev_racing_point(closest_coords, second_closest_coords, car_coords, heading):

            # Virtually set the car more into the heading direction
            heading_vector = [math.cos(math.radians(
                heading)), math.sin(math.radians(heading))]
            new_car_coords = [car_coords[0]+heading_vector[0],
                              car_coords[1]+heading_vector[1]]

            # Calculate distance from new car coords to 2 closest racing points
            distance_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                        x2=closest_coords[0],
                                                        y1=new_car_coords[1],
                                                        y2=closest_coords[1])
            distance_second_closest_coords_new = dist_2_points(x1=new_car_coords[0],
                                                               x2=second_closest_coords[0],
                                                               y1=new_car_coords[1],
                                                               y2=second_closest_coords[1])

            if distance_closest_coords_new <= distance_second_closest_coords_new:
                next_point_coords = closest_coords
                prev_point_coords = second_closest_coords
            else:
                next_point_coords = second_closest_coords
                prev_point_coords = closest_coords

            return [next_point_coords, prev_point_coords]

def racing_direction_diff(closest_coords, second_closest_coords, car_coords, heading):

            # Calculate the direction of the center line based on the closest waypoints
            next_point, prev_point = next_prev_racing_point(closest_coords,
                                                            second_closest_coords,
                                                            car_coords,
                                                            heading)

            # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
            track_direction = math.atan2(
                next_point[1] - prev_point[1], next_point[0] - prev_point[0])

            # Convert to degree
            track_direction = math.degrees(track_direction)

            # Calculate the difference between the track direction and the heading direction of the car
            direction_diff = abs(track_direction - heading)
            if direction_diff > 180:
                direction_diff = 360 - direction_diff

            return direction_diff

def read_params(params):
    global all_wheels_on_track
    global x
    global y
    global DISTANCE_FROM_CENTER
    global is_left_of_center
    global heading
    global progress
    global steps
    global speed
    global steering_angle
    global TRACK_WIDTH
    global waypoints
    global closest_waypoints
    global is_offtrack

    ################## INPUT PARAMETERS ###################
    # Read all input parameters

    all_wheels_on_track = params['all_wheels_on_track']
    x = params['x']
    y = params['y']
    DISTANCE_FROM_CENTER = params['distance_from_center']
    is_left_of_center = params['is_left_of_center']
    heading = params['heading']
    progress = params['progress']
    steps = params['steps']
    speed = params['speed']
    steering_angle = params['steering_angle']
    TRACK_WIDTH = params['track_width']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    is_offtrack = params['is_offtrack']