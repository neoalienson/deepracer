import math

class SETTINGS:
    debug = False
    verbose = True

class TRACK_INFO:
    STANDARD_TIME = 12.0  # seconds (time that is easily done by model)
    FASTEST_TIME = 7.5  # seconds (best time of 1st place on the track)
    MIN_SPEED = 1.3
    MAX_SPEED = 4.0

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
    closest_waypoints = [0, 1]
    is_offtrack = None

# Global
class G:
    direction_diff = None
    optimals = None
    optimals_second = None
    route_direction = None
    normalized_distance_from_route = None
    intermediate_progress_bonus = None
    projected_time = None
    reward_prediction = None
    steps_prediction = None

class STATE:
    prev_speed = None
    prev_steering_angle = None 
    prev_steps = None
    prev_direction_diff = None
    prev_normalized_distance_from_route = None

class REWARDS:
    final = 0.001

def read_params(params):
    ################## INPUT PARAMETERS ###################
    # Read all input parameters
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


def get_distance_reward():
    d = max(1e-3, 1 - (abs(G.dist_to_racing_line)/(P.track_width * 0.8)))
    #Reward reducing distance to the race line
    # distance_reduction_bonus = 1
    if STATE.prev_normalized_distance_from_route is not None:
        if abs(STATE.prev_normalized_distance_from_route) > abs(G.dist_to_racing_line):
            print(f'BONUS: STATE.prev_normalized_distance_from_route > G.dist_to_racing_line: {STATE.prev_normalized_distance_from_route:.1f} > {G.dist_to_racing_line:.1f}')
            return max(d, SETTINGS.MIN_DIST_CLOSING_BONUS)

    return d

def init_state():
    STATE.prev_speed = None
    STATE.prev_steering_angle = None
    STATE.prev_direction_diff = None
    STATE.prev_normalized_distance_from_route = None

def print_params():
    if not SETTINGS.verbose:
        return    

    if STATE.prev_speed is not None:
      print(f"state: sp:{STATE.prev_speed:.1f} st:{STATE.prev_steering_angle:.1f} dd:{STATE.prev_direction_diff:.1f}, dt:{STATE.prev_normalized_distance_from_route:.1f}")
    else:
      print("empty state")

def dist_to_racing_line(closest_coords, second_closest_coords, car_coords):
    # Calculate the distances between 2 closest racing points
    a = abs(dist_2_points(x1=closest_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=closest_coords[1],
                                  y2=second_closest_coords[1]))

    # Distances between car and closest and second closest racing point
    ob = dist_2_points(x1=car_coords[0],
                                  x2=closest_coords[0],
                                  y1=car_coords[1],
                                  y2=closest_coords[1])
    b = abs(ob)
    c = abs(dist_2_points(x1=car_coords[0],
                                  x2=second_closest_coords[0],
                                  y1=car_coords[1],
                                  y2=second_closest_coords[1]))

    # Calculate distance between car and racing line (goes through 2 closest racing points)
    # try-except in case a=0 (rare bug in DeepRacer)
    try:
        distance = (-(a**4) + 2*(a**2)*(b**2) + 2*(a**2)*(c**2) -
                           (b**4) + 2*(b**2)*(c**2) - (c**4))**0.5 / (2*a)
    except:
        distance = ob

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
 
# Gives back indexes that lie between start and end index of a cyclical list 
# (start index is included, end index is not)
def indexes_cyclical(start, end, array_len):
            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]


def reward_function(params):
    read_params(params)

    reset_global()

    # Get closest indexes for racing line (and distances to all points on racing line)
    closest_index, second_closest_index = closest_2_racing_points_index(TRACK_INFO.racing_line, [P.x, P.y])

    # Save first racingpoint of episode for later
    if STATE.first_racingpoint_index is None:
        STATE.first_racingpoint_index = closest_index

    # Get optimal [x, y, speed, time] for closest and second closest index
    G.optimals = TRACK_INFO.racing_line[closest_index]
    G.optimals_second = TRACK_INFO.racing_line[second_closest_index]

    if max(P.closest_waypoints[0], P.closest_waypoints[1]) < len(TRACK_INFO.racing_line):
        G.next_index = min(max(P.closest_waypoints[0], P.closest_waypoints[1]) + 1, 69)
    else:
        G.next_index = 0

    next_point_coords = TRACK_INFO.racing_line[G.next_index]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians between target and current vehicle position
    G.route_direction = math.atan2(next_point_coords[1] - P.y, next_point_coords[0] - P.x) 
    # Convert to degree
    G.route_direction = math.degrees(G.route_direction)
    # Calculate the difference between the track direction and the heading direction of the car
    if (P.heading > 0 and G.route_direction < 0) or (P.heading < 0 and G.route_direction > 0):
        G.direction_diff = G.route_direction + P.heading
    else:
        G.direction_diff = G.route_direction - P.heading

    G.dist_to_racing_line = dist_to_racing_line(G.optimals[0:2], G.optimals_second[0:2], [P.x, P.y])

    # Reinitialize previous parameters if it is a new episode
    if STATE.prev_steps is None or P.steps < STATE.prev_steps:
        init_state()

    is_heading_in_right_direction = True
    #Check if the speed has dropped
    has_speed_dropped = False
    if STATE.prev_speed is not None:
        if STATE.prev_speed > P.speed:
            has_speed_dropped = True

    #Penalize slowing down without good reason on straight portions
    # if has_speed_dropped and not is_turn_upcoming: 
    #     speed_maintain_bonus = min( P.speed / STATE.prev_speed, 1 )
    #Penalize making the heading direction worse
    heading_decrease_bonus = 0
    if STATE.prev_direction_diff is not None and G.direction_diff != 0:
        if is_heading_in_right_direction:
            if abs( STATE.prev_direction_diff / G.direction_diff ) > 1:
                heading_decrease_bonus = min(10, abs( STATE.prev_direction_diff / G.direction_diff ))
    #has the steering angle changed
    has_steering_angle_changed = False
    if STATE.prev_steering_angle is not None:
        if not(math.isclose(STATE.prev_steering_angle,P.steering_angle)):
            has_steering_angle_changed = True
    steering_angle_maintain_bonus = 1 
    #Not changing the steering angle is a good thing if heading in the right direction
    if is_heading_in_right_direction and not has_steering_angle_changed:
        if abs(G.direction_diff) < 10:
            steering_angle_maintain_bonus *= 2
        if abs(G.direction_diff) < 5:
            steering_angle_maintain_bonus *= 2
        if STATE.prev_direction_diff is not None and abs(STATE.prev_direction_diff) > abs(G.direction_diff):
            steering_angle_maintain_bonus *= 2

    G.sigma_speed = abs(TRACK_INFO.MAX_SPEED - TRACK_INFO.MIN_SPEED)/6.0
    OPTIMAL.speed = G.optimals_second[2]

    print_params()

    # Before returning reward, update the variables
    STATE.prev_speed = P.speed
    STATE.prev_steering_angle = P.steering_angle
    STATE.prev_direction_diff = G.direction_diff
    STATE.prev_steps = P.steps
    STATE.prev_normalized_distance_from_route = G.dist_to_racing_line

    return float(REWARDS.final)
