import math


class Reward:
    # original 1
    BASE_REWARD = 1e-3
    ################ Reward Weighting  ###############################
    # original 2
    SPEED_MULTIPLIER = 0
    # original 1
    STEP_MULTIPLIER = 1
    # original 1
    DISTANCE_MULTIPLIER = 3
    ##################################################################

    #### 0 for no reduction, 1 to reduce speed to zero ###############
    SPEED_REDUCTION = 0
    OVER_SPEED_REWARD = 0

    SPEED_DIFF_NO_REWARD = 1
    REWARD_PER_STEP_FOR_FASTEST_TIME = 1 
    REWARD_FOR_FASTEST_TIME = 1500 # should be adapted to track length and other rewards
    STANDARD_TIME = 13  # seconds (time that is easily done by model)
    FASTEST_TIME = 9  # seconds (best time of 1st place on the track)

    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose
        self.warning = ""

    def cal_speed_reward(self, optimals, speed):
        speed_diff = (optimals[2] * (1 - self.SPEED_REDUCTION))-speed
        if abs(speed_diff) <= self.SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (abs(speed_diff)/(self.SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
#        if self.verbose == True:
            # Speed, Optimal Speed, Reward reward (w/out multiple), Speed Difference
#            print(f"s: {speed} , so: {optimals[2]}, sr: {speed_reward:.3f}, sd: {speed_diff:.3f}")
        
        if speed_diff < 0:
            speed_reward = speed_reward * self.OVER_SPEED_REWARD
            self.warning = f"OVER SPEED for {speed_diff:.2f} {self.warning}"

        return speed_reward

    def reward_function(self, params):
        # Import package (needed for heading)
        import math

        ################## HELPER FUNCTIONS ###################

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

        # Calculate how long car would take for entire lap, if it continued like it did until now
        def projected_time(first_index, closest_index, step_count, times_list):
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

        #################### RESET ############################
        self.warning = ""

        #################### RACING LINE ######################

        # Optimal racing line for the Spain track
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [
            [3.06664, 0.69989, 4.0, 0.03654],
            [3.21372, 0.69357, 4.0, 0.0368],
            [3.36169, 0.6893, 4.0, 0.03701],
            [3.51032, 0.68657, 4.0, 0.03716],
            [3.6594, 0.68496, 4.0, 0.03727],
            [3.8088, 0.68412, 4.0, 0.03735],
            [3.9584, 0.68379, 4.0, 0.0374],
            [4.10793, 0.68414, 4.0, 0.03738],
            [4.25712, 0.68535, 4.0, 0.0373],
            [4.40585, 0.68761, 4.0, 0.03719],
            [4.55396, 0.69115, 4.0, 0.03704],
            [4.70133, 0.69619, 4.0, 0.03686],
            [4.84783, 0.70293, 4.0, 0.03666],
            [4.99331, 0.71158, 3.93749, 0.03701],
            [5.13763, 0.72237, 3.59367, 0.04027],
            [5.28066, 0.73548, 3.26778, 0.04395],
            [5.42227, 0.75106, 2.95403, 0.04823],
            [5.56233, 0.76926, 2.65651, 0.05317],
            [5.70059, 0.79043, 2.37378, 0.05892],
            [5.83677, 0.81492, 2.10295, 0.06579],
            [5.97044, 0.84325, 1.86318, 0.07334],
            [6.10109, 0.87602, 1.64716, 0.08178],
            [6.22807, 0.91394, 1.43277, 0.09249],
            [6.35051, 0.95783, 1.43277, 0.09078],
            [6.46729, 1.00867, 1.43277, 0.0889],
            [6.57689, 1.06758, 1.43277, 0.08684],
            [6.67731, 1.1357, 1.3, 0.09334],
            [6.76588, 1.21406, 1.3, 0.09097],
            [6.83839, 1.3035, 1.3, 0.08856],
            [6.8965, 1.40041, 1.3, 0.08693],
            [6.94112, 1.50274, 1.3, 0.08587],
            [6.96947, 1.60974, 1.3, 0.08515],
            [6.97707, 1.71948, 1.40874, 0.07809],
            [6.96702, 1.82873, 1.42441, 0.07702],
            [6.94149, 1.93565, 1.42441, 0.07717],
            [6.90175, 2.03894, 1.42441, 0.0777],
            [6.84699, 2.13674, 1.42441, 0.07869],
            [6.77574, 2.22619, 1.5742, 0.07264],
            [6.69117, 2.307, 1.75211, 0.06676],
            [6.5958, 2.37958, 1.95561, 0.06129],
            [6.49161, 2.44467, 2.23061, 0.05507],
            [6.38049, 2.50335, 2.5043, 0.05018],
            [6.26371, 2.5565, 2.84885, 0.04504],
            [6.14243, 2.60505, 3.3309, 0.03922],
            [6.01777, 2.65004, 4.0, 0.03313],
            [5.89082, 2.69257, 4.0, 0.03347],
            [5.76272, 2.73384, 4.0, 0.03365],
            [5.63017, 2.77782, 4.0, 0.03491],
            [5.49811, 2.82317, 4.0, 0.03491],
            [5.36667, 2.87018, 4.0, 0.0349],
            [5.23602, 2.9192, 4.0, 0.03489],
            [5.10632, 2.97055, 4.0, 0.03487],
            [4.97777, 3.02458, 4.0, 0.03486],
            [4.85051, 3.08159, 4.0, 0.03486],
            [4.72465, 3.14171, 4.0, 0.03487],
            [4.60022, 3.20493, 4.0, 0.03489],
            [4.47719, 3.27112, 4.0, 0.03493],
            [4.35549, 3.34005, 4.0, 0.03497],
            [4.23502, 3.41139, 4.0, 0.035],
            [4.11568, 3.48475, 4.0, 0.03502],
            [3.99733, 3.55968, 4.0, 0.03502],
            [3.87982, 3.63569, 3.45946, 0.04046],
            [3.76284, 3.71231, 2.94803, 0.04743],
            [3.64732, 3.78753, 2.56815, 0.05367],
            [3.53132, 3.86145, 2.23647, 0.06151],
            [3.41449, 3.93319, 2.23647, 0.0613],
            [3.29649, 4.00174, 2.23647, 0.06102],
            [3.17696, 4.06601, 2.23647, 0.06068],
            [3.05548, 4.12441, 2.23647, 0.06027],
            [2.93169, 4.17515, 2.23647, 0.05982],
            [2.80549, 4.21581, 2.46695, 0.05375],
            [2.67785, 4.24822, 2.56094, 0.05142],
            [2.5493, 4.27301, 2.47357, 0.05293],
            [2.42021, 4.29067, 2.35598, 0.0553],
            [2.29093, 4.30153, 2.13864, 0.06067],
            [2.16175, 4.30562, 1.95082, 0.06625],
            [2.03303, 4.30283, 1.74656, 0.07372],
            [1.90519, 4.29292, 1.53607, 0.08347],
            [1.7788, 4.27535, 1.42134, 0.08977],
            [1.65459, 4.24957, 1.42134, 0.08926],
            [1.53376, 4.21418, 1.42134, 0.08859],
            [1.41797, 4.16786, 1.42134, 0.08774],
            [1.30974, 4.10893, 1.42134, 0.0867],
            [1.21287, 4.03538, 1.42134, 0.08557],
            [1.13093, 3.94692, 1.46468, 0.08233],
            [1.06435, 3.84609, 1.62451, 0.07438],
            [1.01121, 3.73603, 1.78792, 0.06836],
            [0.96999, 3.61869, 1.95188, 0.06372],
            [0.93956, 3.49541, 2.13059, 0.0596],
            [0.91891, 3.36729, 2.32352, 0.05585],
            [0.90708, 3.23527, 2.51124, 0.05278],
            [0.90334, 3.10018, 2.7333, 0.04944],
            [0.90681, 2.9629, 2.89511, 0.04743],
            [0.91698, 2.82419, 3.02951, 0.04591],
            [0.93341, 2.68483, 3.13796, 0.04472],
            [0.95571, 2.54557, 3.1355, 0.04498],
            [0.98342, 2.40706, 2.97575, 0.04747],
            [1.01626, 2.26986, 2.77801, 0.05078],
            [1.05392, 2.13444, 2.53449, 0.05546],
            [1.09624, 2.00121, 2.30368, 0.06068],
            [1.14311, 1.87057, 2.07354, 0.06694],
            [1.19482, 1.7431, 1.84356, 0.07462],
            [1.25158, 1.61938, 1.61408, 0.08433],
            [1.31382, 1.50015, 1.61408, 0.08333],
            [1.38221, 1.38643, 1.61408, 0.08222],
            [1.45757, 1.27943, 1.61408, 0.08108],
            [1.54096, 1.18072, 1.61408, 0.08006],
            [1.63386, 1.09253, 1.61408, 0.07936],
            [1.7384, 1.01844, 1.90143, 0.06739],
            [1.85098, 0.955, 2.10775, 0.06131],
            [1.97002, 0.90067, 2.28389, 0.0573],
            [2.09459, 0.85453, 2.4714, 0.05375],
            [2.2239, 0.81579, 2.67564, 0.05045],
            [2.35729, 0.78373, 2.89947, 0.04732],
            [2.49419, 0.75767, 3.15191, 0.04421],
            [2.63406, 0.73695, 3.45884, 0.04088],
            [2.77639, 0.72086, 3.80768, 0.03762],
            [2.92074, 0.70874, 4.0, 0.03621]]        

        ################## INPUT PARAMETERS ###################

        # Read all input parameters
        all_wheels_on_track = params['all_wheels_on_track']
        x = params['x']
        y = params['y']
        distance_from_center = params['distance_from_center']
        is_left_of_center = params['is_left_of_center']
        heading = params['heading']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering_angle = params['steering_angle']
        track_width = params['track_width']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        is_offtrack = params['is_offtrack']

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])
        if self.verbose == True:
          print(f'x: {x:.2f}, y: {y:.2f}, dc: {distance_from_center:.2f}, il: {is_left_of_center}, h: {heading:.2f}, p: {progress:.2f}, st: {steps:3.0f}, sp: {speed:.2f}, sa: {steering_angle:.2f}, tw: {track_width:.2f}, cw: {closest_waypoints}, ot: {is_offtrack}, 1c: {closest_index}, 2c: {second_closest_index}')

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        # Save first racingpoint of episode for later
        if steps == 1 or self.first_racingpoint_index is None:
            self.first_racingpoint_index = closest_index

        ################ REWARD AND PUNISHMENT ################

        ## Define the default reward ##
        reward = self.BASE_REWARD

        ## Reward if car goes close to optimal racing line ##
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))
        reward += distance_reward * self.DISTANCE_MULTIPLIER
        ## Reward if speed is close to optimal speed ##

        speed_reward = self.cal_speed_reward(optimals, speed)
        reward += speed_reward * self.SPEED_MULTIPLIER

        # Reward if less steps
        times_list = [row[3] for row in racing_track]
        projected_time = projected_time(self.first_racingpoint_index, closest_index, steps, times_list)
        try:
            steps_prediction = projected_time * 15 + 1
            reward_prediction = max(1e-3, (-self.REWARD_PER_STEP_FOR_FASTEST_TIME * (self.FASTEST_TIME) /
                                           (self.STANDARD_TIME - self.FASTEST_TIME))*(steps_prediction - (self.STANDARD_TIME*15+1)))
            steps_reward = min(self.REWARD_PER_STEP_FOR_FASTEST_TIME, reward_prediction / steps_prediction)
        except:
            steps_reward = 0
        reward += steps_reward * self.STEP_MULTIPLIER

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if direction_diff > 30:
            reward = 1e-3
            self.warning = f"WRONG DIRECTION: {direction_diff:.1f} {self.warning}"

        # Zero reward of obviously too slow unless it is being reset
        speed_diff_zero = optimals[2] - speed
        if speed_diff_zero > 0.5 and steps > 10:
            reward = 1e-3
            self.warning = f"TOO SLOW: {speed_diff_zero:.2f} {self.warning}"
            
        ## Incentive for finishing the lap in less steps ##
        if progress == 100:
            finish_reward = max(1e-3, (-self.REWARD_FOR_FASTEST_TIME /
                      (15*(self.STANDARD_TIME - self.FASTEST_TIME)))*(steps-self.STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward += finish_reward
        
        ## Zero reward if off track ##
        if not all_wheels_on_track:
            reward = 1e-3
            self.warning = f"OFF TRACK {self.warning}"

        ####################### VERBOSE #######################
        if self.verbose == True:
            # Closest index, Distance to racing line, Distance reward (w/out multiple), Direction difference
            # Predicted time, Steps reward, Finish reward, Reward
            print(f"fr: {finish_reward:.2f}, dr: {distance_reward:.3f}, tr: {steps_reward:.2f}, sr: {speed_reward:.2f},  r: {reward:.2f}, ci: {closest_index}, dl: {dist:.3f},  dd: {direction_diff:.3f}, pt: {projected_time:.2f}")
            print(self.warning)
            
        return float(reward)

reward_object = Reward(verbose=True) # add parameter verbose=True to get noisy output for testing

def reward_function(params):
    return reward_object.reward_function(params)