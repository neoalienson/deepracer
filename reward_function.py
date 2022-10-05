import math

class SETTINGS:
    debug = False
    verbose = True

class CONFIGS:
    STAGE = 1
    REWARD_FOR_FASTEST_TIME = 500 # should be adapted to track length and other rewards. finish_reward = max(1e-3, (-self.REWARD_FOR_FASTEST_TIME / (15*(self.STANDARD_TIME - self.FASTEST_TIME)))*(steps-self.STANDARD_TIME*15))
    DISTANCE_MULTIPLIER = 1
    STEERING_MULTIPLIER = 0.5
    SPEED_MULTIPLIER    = 1
    PROGRESS_MULTIPLIER = 0.5
    STEP_MULTIPLIER     = 1

class TRACK_INFO:
    STANDARD_TIME = 12.5  # seconds (time that is easily done by model)
    FASTEST_TIME = 7.3  # seconds (best time of 1st place on the track)
    MIN_SPEED = 1.3
    MAX_SPEED = 4.0
    #################### RACING LINE ######################
    # Optimal racing line for the Spain track
    # Each row: [x,y,speed,timeFromPreviousPoint]
    racing_line = [
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

# Global
class G:
    direction_diff = None
    optimals = None
    optimals_second = None
    route_direction = None
    sigma_speed = None
    normalized_distance_from_route = None
    dist_from_racinig_line = None
    intermediate_progress = [0] * 71
    next_index = None
    intermediate_progress_bonus = None

def reward_function(params):
    read_params(params)

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

    G.dist_from_racing_line = dist_to_racing_line(G.optimals[0:2], G.optimals_second[0:2], [P.x, P.y])

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

    if SETTINGS.debug:
        print_state()

    G.sigma_speed = abs(TRACK_INFO.MAX_SPEED - TRACK_INFO.MIN_SPEED)/6.0
    OPTIMAL.speed = G.optimals_second[2]

    ## Reward if car goes close to optimal racing line ##
    # G.normalized_distance_from_route = G.dist_from_racinig_line
    REWARDS.heading = get_heading_reward()
    REWARDS.distance = get_distance_reward()
    REWARDS.speed = get_speed_reward()

    # Before returning reward, update the variables
    STATE.prev_speed = P.speed
    STATE.prev_steering_angle = P.steering_angle
    STATE.prev_direction_diff = G.direction_diff
    STATE.prev_steps = P.steps
    STATE.prev_normalized_distance_from_route = G.dist_from_racinig_line

    REWARDS.immediate = get_immediate_reward()

    # Reward for making steady progress
    G.intermediate_progress_bonus = 0
    REWARDS.progress = 0
    # REWARDS.progress = 10 * P.progress / P.steps
    # if P.steps <= 5:
    #     REWARDS.progress = 1 #ignore progress in the first 5 steps
    # # Bonus that the agent gets for completing every 10 percent of track
    # # Is exponential in the progress / steps. 
    # # exponent increases with an increase in fraction of lap completed
    # pi = int(P.progress//10)
    # if pi != 0 and G.intermediate_progress[ pi ] == 0:
    #     if pi==10: # 100% track completion
    #         G.intermediate_progress_bonus = REWARDS.progress ** 14
    #     else:
    #         G.intermediate_progress_bonus = REWARDS.progress ** (5+0.75*pi)
    # G.intermediate_progress[ pi ] = G.intermediate_progress_bonus
    times_list = [row[3] for row in TRACK_INFO.racing_line]
    projected_time = get_projected_time(STATE.first_racingpoint_index, closest_index, P.steps, times_list)
    try:
        steps_prediction = projected_time * 15 + 1
        reward_prediction = max(1e-3, (-SETTINGS.REWARD_PER_STEP_FOR_FASTEST_TIME * (SETTINGS.FASTEST_TIME) /
                                       (SETTINGS.STANDARD_TIME - SETTINGS.FASTEST_TIME))*(steps_prediction - (SETTINGS.STANDARD_TIME*15+1)))
        REWARDS.progress = min(SETTINGS.REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction)
    except:
        REWARDS.progress = 0

    REWARDS.final = get_final_reward()
    print_params()

    return float(REWARDS.final)

def get_distance_reward():
    #Reward reducing distance to the race line
    # distance_reduction_bonus = 1
    # if STATE.prev_normalized_distance_from_route is not None and STATE.prev_normalized_distance_from_route > G.normalized_distance_from_route:
    #     if abs(G.normalized_distance_from_route) > 0:
    #         distance_reduction_bonus = min( abs( STATE.prev_normalized_distance_from_route / G.normalized_distance_from_route ), 2)
    
    # return 1
    #distance reward is value of the standard normal scaled back to 1. 
    #Hence the 1/2*pi*sigma term is cancelled out
#    sigma=abs(normalized_route_distance_from_inner_border / 4) 
#  return math.exp(-0.5*abs(normalized_car_distance_from_route)**2/G.sigma**2)
    return max(1e-3, 1 - (G.dist_from_racing_line/(P.track_width * 0.5)))

def get_heading_reward():
    if abs(G.direction_diff) <= 20:
        return math.cos( abs(G.direction_diff ) * ( math.pi / 180 ) ) ** 4
    return math.cos( abs(G.direction_diff ) * ( math.pi / 180 ) ) ** 10

def get_speed_reward():
    return math.exp(-0.5*abs(P.speed - OPTIMAL.speed)**2 / G.sigma_speed**2)

def get_final_reward():
    if P.is_offtrack:
        return 0.001
        if SETTINGS.verbose:
            print(f"OFF TRACK")
#    return max(REWARDS.immediate + G.intermediate_progress_bonus, 1e-3)
    return max(REWARDS.immediate + REWARDS.progress, 1e-3)

def get_immediate_reward():
    lc = (REWARDS.speed + REWARDS.distance + REWARDS.heading) ** 2 + ( REWARDS.speed * REWARDS.distance * REWARDS.heading )

    # Zero reward if obviously wrong direction (e.g. spin)
    # below cannot tell diff is right or left
    # P.direction_diff = racing_direction_diff(P.optimals[0:2], P.optimals_second[0:2], [P.x, P.y], P.heading)
    if abs(G.direction_diff) > 60:
        if SETTINGS.verbose:
            print(f"!!! FAR AWAY FROM DIRECTION: {G.direction_diff:.1f}")
        return 0

    # prohibit left turn between waypoints
    if is_right_turn_section() and P.steering_angle > 0:
        if SETTINGS.verbose:
            print(f"!!! SHOULD NOT MAKE LEFT TURN IN RIGHT TURN SECTION")
        return 0

    if is_left_turn_section() and P.steering_angle < 0:
        if SETTINGS.verbose:
            print(f"!!! SHOULD NOT MAKE RIGHT TURN IN LEFT TURN SECTION")
        return 0

    # avoid sharp turn if previous speed is fast
    if STATE.speed > 2.3 and abs(P.steering_angle > 20)
        if SETTINGS.verbose:
            print(f"!!! SHOULD NOT MAKE SHARP TURN IF PREVIOUS SPEED IS TOO FAST")
        return 0

    if CONFIGS.STAGE > 1 and OPTIMAL.speed - P.speed > 1.5 and is_straight_section:
        if SETTINGS.verbose:
            print(f"!!! TOO SLOW")
        return lc / 2

    if not is_right_turn_section():
        if P.speed - OPTIMAL.speed > 1 or (CONFIGS.STAGE == 1 and P.speed > 2.3):
            if SETTINGS.verbose:
                print(f"!!! TOO FAST")
            return lc / 3

    return max(lc, 1e-3)

def is_right_turn_section():
    return (P.closest_waypoints[0] > 25 or P.closest_waypoints[1] > 25) and (P.closest_waypoints[0] < 34 or P.closest_waypoints[1] < 34)

def is_left_turn_section():
    return (P.closest_waypoints[0] > 10 or P.closest_waypoints[1] > 10) and (P.closest_waypoints[0] < 23 or P.closest_waypoints[1] < 23) or \
        (P.closest_waypoints[0] > 40 or P.closest_waypoints[1] > 40) and (P.closest_waypoints[0] < 43 or P.closest_waypoints[1] < 43) or \
        (P.closest_waypoints[0] > 49 or P.closest_waypoints[1] > 49) and (P.closest_waypoints[0] < 52 or P.closest_waypoints[1] < 52) or \
        (P.closest_waypoints[0] > 61 or P.closest_waypoints[1] > 61) and (P.closest_waypoints[0] < 67 or P.closest_waypoints[1] < 67)

def is_straight_section():
    return (P.closest_waypoints[0] > 68 or P.closest_waypoints[1] > 68) or (P.closest_waypoints[0] < 10 or P.closest_waypoints[1] < 10) or \
        (P.closest_waypoints[0] > 53 or P.closest_waypoints[1] > 53) and (P.closest_waypoints[0] < 60 or P.closest_waypoints[1] < 60)

def print_state():
    if not SETTINGS.verbose:
        return
    if STATE.prev_speed is not None:
      print(f"state: sp:{STATE.prev_speed:.1f} st:{STATE.prev_steering_angle:.1f} dd:{STATE.prev_direction_diff:.1f}")
    else:
      print("empty state")

def init_state():
    STATE.prev_speed = None
    STATE.prev_steering_angle = None
    STATE.prev_direction_diff = None
    STATE.prev_normalized_distance_from_route = None

def print_params():
    if not SETTINGS.verbose:
        return    
    import math
    FINAL_BAR_LENGTH = 10
    SPEED_BAR_LENGTH = 5 
    capped_final = min(REWARDS.final, FINAL_BAR_LENGTH)
    print(f"r:{REWARDS.final:.2f} {'*' * math.ceil(capped_final*1)}{' ' * math.floor(FINAL_BAR_LENGTH-capped_final*1)}", end =" ")
    capped_speed = min(REWARDS.speed, SPEED_BAR_LENGTH)
    normalized_speed = (REWARDS.speed - 1.3) * SPEED_BAR_LENGTH / 4.0
    print(f"sr:{REWARDS.speed:.1f} {'*' * math.ceil(normalized_speed)}{' ' * math.floor(SPEED_BAR_LENGTH-normalized_speed)}", end =" ")
    print(f"dr:{REWARDS.distance:.1f} {'*' * math.ceil(REWARDS.distance*10)}{' ' * math.floor(10-REWARDS.distance*10)}", end =" ")
    print(f"hr:{REWARDS.heading:.1f} {'*' * math.ceil(REWARDS.heading*2.5)}{' ' * math.floor(10-REWARDS.heading*2.5)}", end =" ")
    print(f"pr:{REWARDS.progress:.1f}", end =" ")
    speed_bar = (P.speed - 1.3) * 10.0 / (4.0 - 1.3)            
    print(f'sp:{P.speed:.1f} {"=" * math.ceil(speed_bar)}{" " * math.floor(10 - speed_bar)}', end = ' ')
    _l = max(0, P.steering_angle / 3)
    print(f'sa:{P.steering_angle:5.1f} {" " * math.floor(10 - _l)}{"<" * math.ceil(_l)}', end = '|')
    _r = max(0, P.steering_angle / -3)
    print(f'{">" * math.ceil(_r)}{" " * math.floor(10 - _r)}', end = ' ')
    print(f'x:{P.x:.1f}, y:{P.y:.1f}, h:{P.heading:.1f}, sr:{REWARDS.steps:.1f}, dr:{REWARDS.distance:.1f}, hr:{REWARDS.heading:.1f}, pr:{REWARDS.progress:.1f}, mr:{REWARDS.immediate:.1f}, ir:{G.intermediate_progress_bonus:.1f}, os:{OPTIMAL.speed:.1f}, dd:{G.direction_diff:.1f}, rd:{G.route_direction:.1f} ni:{G.next_index}')
    if SETTINGS.debug:
        print(f'dc: {P.distance_from_center:.2f}, p:{P.progress:.2f}, st:{P.steps:3.0f}, cw:{P.closest_waypoints}, rd:{G.route_direction:.1f}, aw: {P.all_wheels_on_track}, il: {P.is_left_of_center}, 2ox:{G.optimals_second[0]}, 2oy:{G.optimals_second[1]}')
        print(f'ot: {P.is_offtrack}, tw: {P.track_width:.2f}, ni: {G.next_index}, {TRACK_INFO.racing_line[G.next_index]}')

    print(f"{{'all_wheels_on_track':{P.all_wheels_on_track},'x':{P.x},'y':{P.y},'distance_from_center':{P.distance_from_center},'is_left_of_center':{P.is_left_of_center},'heading':{P.heading},'progress':{P.progress},'steps':{P.steps},'speed':{P.speed},'steering_angle':{P.steering_angle},'track_width':{P.track_width},'waypoints':self.waypoints ,'closest_waypoints':{P.closest_waypoints},'is_offtrack':{P.is_offtrack}}}")
     
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
 
# Gives back indexes that lie between start and end index of a cyclical list 
# (start index is included, end index is not)
def indexes_cyclical(start, end, array_len):
            if end < start:
                end += array_len

            return [index % array_len for index in range(start, end)]

# Calculate how long car would take for entire lap, if it continued like it did until now
def get_projected_time(first_index, closest_index, step_count, times_list):
            # Calculate how much time has passed since start
            current_actual_time = (step_count-1) / 15

            # Calculate which indexes were already passed
            indexes_traveled = indexes_cyclical(first_index, closest_index, len(times_list))

            # Calculate how much time should have passed if car would have followed optimals
            current_expected_time = sum([times_list[i] for i in indexes_traveled])

            # Calculate how long one entire lap takes if car follows optimals
            total_expected_time = sum(times_list)

            # Calculate how long car would take for entire lap, if it continued like it did until now
            try:
                projected_time = (current_actual_time/current_expected_time) * total_expected_time
            except:
                projected_time = 9999

            return projected_time

class STATE:
    prev_speed = None
    prev_steering_angle = None 
    prev_steps = None
    prev_direction_diff = None
    prev_normalized_distance_from_route = None
    first_racingpoint_index = None

class REWARDS:
    final = 0.001
    speed = 0
    distance = 0
    steps = 0
    progress = 0
    immediate = 0

class OPTIMAL:
    speed = 0

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