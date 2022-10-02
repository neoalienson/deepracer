def reward_function(params, verbose=False):
    setup(verbose)
    read_params(params)

    abs_steering = abs(STEERING_ANGLE) # Only need the absolute steering angle

    # Steering threshold
    ABS_STEERING_THRESHOLD = 5

    reward = 0.001

    if params["all_wheels_on_track"]:
        reward += 1

    # reward if steer less
    if abs_steering < ABS_STEERING_THRESHOLD:
        reward += 1
   
    reward += ( params["speed"] / 8 )
   
    return float(reward)

def setup(verbose):
    global VERBOSE
    global DEBUG
    VERBOSE = verbose
    DEBUG = False

def print_params():
    if not VERBOSE:
        return
        
    import math

    speed_bar = (speed - 1.3) * 10.0 / (4.0 - 1.3)            
    print(f'sp: {speed:.1f} {"=" * math.ceil(speed_bar)}{" " * math.floor(10 - speed_bar)}', end = ' ')
    _l = max(0, STEERING_ANGLE / 3)
    print(f'sa: {STEERING_ANGLE:5.1f} {" " * math.floor(10 - _l)}{"<" * math.ceil(_l)}', end = '|')
    _r = max(0, STEERING_ANGLE / -3)
    print(f'{">" * math.ceil(_r)}{" " * math.floor(10 - _r)}', end = ' ')
    print(f'x: {x:.1f}, y: {y:.1f}, h: {heading:.1f}')
    if DEBUG == True:
        print(f'dc: {DISTANCE_FROM_CENTER:.2f}, p: {progress:.2f}, st: {steps:3.0f}, cw: {closest_waypoints}, 1c: {closest_index}, 2c: {second_closest_index}, aw: {all_wheels_on_track}, il: {is_left_of_center}, ')
        print(f'ot: {is_offtrack}, tw: {TRACK_WIDTH:.2f}')
    
def read_params(params):
    ################## INPUT PARAMETERS ###################
    # Read all input parameters
    global all_wheels_on_track
    global x
    global y
    global DISTANCE_FROM_CENTER
    global is_left_of_center
    global heading
    global progress
    global steps
    global speed
    global STEERING_ANGLE
    global TRACK_WIDTH
    global waypoints
    global closest_waypoints
    global is_offtrack

    all_wheels_on_track = params['all_wheels_on_track']
    x = params['x']
    y = params['y']
    DISTANCE_FROM_CENTER = params['distance_from_center']
    is_left_of_center = params['is_left_of_center']
    heading = params['heading']
    progress = params['progress']
    steps = params['steps']
    speed = params['speed']
    STEERING_ANGLE = params['steering_angle']
    TRACK_WIDTH = params['track_width']
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    is_offtrack = params['is_offtrack']