import math

class SETTINGS:
    verbose = False
    debug = False
    REWARD_FOR_FASTEST_TIME = 500 # should be adapted to track length and other rewards. finish_reward = max(1e-3, (-self.REWARD_FOR_FASTEST_TIME / (15*(self.STANDARD_TIME - self.FASTEST_TIME)))*(steps-self.STANDARD_TIME*15))
    STANDARD_TIME = 12.5  # seconds (time that is easily done by model)
    FASTEST_TIME = 8.3  # seconds (best time of 1st place on the track)
    REWARD_PER_STEP_FOR_FASTEST_TIME = 1
    STAGE = 1
    DISTANCE_MULTIPLIER = 1
    STEERING_MULTIPLIER = 0.5
    SPEED_MULTIPLIER    = 0
    PROGRESS_MULTIPLIER = 0.5
    
class P:
    all_wheels_on_track = None
    x = None
    y = None
    distance_from_center = None
    is_left_of_center = None
    heading = None
    progress = None
    steps = None
    speed = None
    steering_angle = None
    track_width = None
    waypoints = None
    closest_waypoints = None
    is_offtrack = None

class G:
    reward = 0
    distance_reward = 0
    speed_reward = 0
    steps_reward = 0

def reward_function(params):
    if SETTINGS.STAGE == 2:
      SETTINGS.DISTANCE_MULTIPLIER = 1
      SETTINGS.STEERING_MULTIPLIER = 0.5
      SETTINGS.SPEED_MULTIPLIER    = 1
      SETTINGS.PROGRESS_MULTIPLIER = 0.5

    read_params(params)

    #################### RACING LINE ######################
    # Optimal racing line for the Spain track
    # Each row: [x,y,speed,timeFromPreviousPoint]
    racing_track = [
        [2.89961, 0.63419, 3.71852, 0.07995],
        [3.17179, 0.61467, 4.0, 0.06822],
        [3.41521, 0.60513, 4.0, 0.0609],
        [3.66934, 0.60052, 3.57157, 0.07117],
        [4.19, 0.6, 2.74444, 0.18971],
        [4.42913, 0.60097, 2.58202, 0.09262],
        [4.67601, 0.6031, 2.30611, 0.10706],
        [5.09007, 0.61172, 2.09622, 0.19757],
        [5.4765, 0.63585, 1.86679, 0.20741],
        [5.78236, 0.67526, 1.65708, 0.1861],
        [6.02754, 0.72951, 1.48022, 0.16965],
        [6.2377, 0.79522, 1.38974, 0.15844],
        [6.4204, 0.87202, 1.38974, 0.14261],
        [6.58033, 0.95991, 1.38974, 0.13131],
        [6.71905, 1.05998, 1.32477, 0.12911],
        [6.8363, 1.17414, 1.32477, 0.12353],
        [6.92973, 1.30502, 1.3, 0.1237],
        [6.99572, 1.45378, 1.3, 0.12518],
        [7.03659, 1.61577, 1.3, 0.12852],
        [7.04462, 1.78987, 1.3, 0.13406],
        [7.00791, 1.97027, 1.3, 0.14161],
        [6.92787, 2.14729, 1.3, 0.14944],
        [6.79056, 2.30578, 1.63, 0.12866],
        [6.61696, 2.44093, 1.83702, 0.11976],
        [6.41789, 2.5501, 2.14869, 0.10566],
        [6.20393, 2.63605, 2.57572, 0.08952],
        [5.98215, 2.70413, 2.77389, 0.08363],
        [5.7567, 2.7606, 2.394, 0.09708],
        [5.55145, 2.80578, 2.394, 0.08779],
        [5.34895, 2.85755, 2.394, 0.08731],
        [5.14951, 2.91749, 2.394, 0.08699],
        [4.95332, 2.98736, 2.394, 0.08699],
        [4.76075, 3.07052, 2.394, 0.08762],
        [4.57215, 3.17281, 2.76076, 0.07772],
        [4.38627, 3.29085, 3.28868, 0.06696],
        [4.20245, 3.42082, 2.79144, 0.08065],
        [4.02012, 3.55894, 2.47953, 0.09225],
        [3.83856, 3.70124, 2.32089, 0.09939],
        [3.68557, 3.81836, 2.26765, 0.08497],
        [3.53186, 3.92981, 2.26765, 0.08372],
        [3.37677, 4.03275, 2.26765, 0.08209],
        [3.21931, 4.12479, 2.26765, 0.08043],
        [3.05818, 4.2042, 2.24987, 0.07984],
        [2.89192, 4.27015, 2.09074, 0.08555],
        [2.71903, 4.32236, 1.92794, 0.09368],
        [2.5383, 4.36112, 1.76543, 0.1047],
        [2.34813, 4.3858, 1.5736, 0.12186],
        [2.1457, 4.39373, 1.47203, 0.13762],
        [1.92732, 4.38033, 1.47203, 0.14863],
        [1.68682, 4.33425, 1.47203, 0.16635],
        [1.42305, 4.23483, 1.47203, 0.1915],
        [1.16077, 4.05832, 1.47203, 0.21477],
        [0.95059, 3.7847, 1.47203, 0.23439],
        [0.8571, 3.41714, 1.99133, 0.19046],
        [0.84863, 3.05629, 2.43775, 0.14807],
        [0.8784, 2.7782, 2.4815, 0.11271],
        [0.91336, 2.56565, 2.20001, 0.09791],
        [0.96322, 2.30877, 1.96315, 0.13329],
        [1.01113, 2.10002, 1.77021, 0.12099],
        [1.06732, 1.89863, 1.55703, 0.13428],
        [1.13422, 1.70558, 1.55703, 0.13122],
        [1.21309, 1.52521, 1.55703, 0.12643],
        [1.30447, 1.36111, 1.55703, 0.12063],
        [1.40944, 1.21507, 1.55703, 0.11551],
        [1.5309, 1.08738, 1.55703, 0.11318],
        [1.67952, 0.9788, 1.87307, 0.09826],
        [1.85659, 0.88246, 2.12097, 0.09504],
        [2.06749, 0.79743, 2.38168, 0.09548],
        [2.31836, 0.72547, 2.74539, 0.09506],
        [2.60449, 0.67017, 3.19474, 0.09122]]

    # Get closest indexes for racing line (and distances to all points on racing line)
    closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [P.x, P.y])

    # Get optimal [x, y, speed, time] for closest and second closest index
    optimals = racing_track[closest_index]
    optimals_second = racing_track[second_closest_index]

    G.reward = 0.001
    
    ## Incentive for finishing the lap in less steps ##
    if P.progress == 100:
        return max(1e-3, (-REWARD_FOR_FASTEST_TIME /
            (15*(STANDARD_TIME - FASTEST_TIME)))*(P.steps-STANDARD_TIME*15))
            
    ## Reward if car goes close to optimal racing line ##
    dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [P.x, P.y])
    G.distance_reward = max(1e-3, 1 - (dist/(P.track_width*0.8)))
    G.reward += G.distance_reward * SETTINGS.DISTANCE_MULTIPLIER
    
    G.reward += SETTINGS.PROGRESS_MULTIPLIER


    if P.all_wheels_on_track == False:
        G.reward = 0.001
        if SETTINGS.verbose:
            print(f"OFF TRACK")

    # Zero reward if obviously wrong direction (e.g. spin)
    direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [P.x, P.y], P.heading)
    if direction_diff > 30:
        G.reward = 0.001
        if SETTINGS.verbose:
            print(f"WRONG DIRECTION: {direction_diff:.1f}")

    return float(G.reward)

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

# Gives back indexes that lie between start and end index of a cyclical list 
# (start index is included, end index is not)
def indexes_cyclical(start, end, array_len):
    if end < start:
        end += array_len
    return [index % array_len for index in range(start, end)]

def read_params(params):
    P.all_wheels_on_track = params['all_wheels_on_track']
    P.x = params['x']
    P.y = params['y']
    P.distance_from_center = params['distance_from_center']
    P.is_left_of_center = params['is_left_of_center']
    P.heading = params['heading']
    P.progress = params['progress']
    P.steps = params['steps']
    P.speed = params['speed']
    P.steering_angle = params['steering_angle']
    P.track_width = params['track_width']
    P.waypoints = params['waypoints']
    P.closest_waypoints = params['closest_waypoints']
    P.is_offtrack = params['is_offtrack']