import math


class Reward:
    # original 1
    BASE_REWARD = 1e-3
    ################ Reward Weighting  ###############################
    # original 2
    SPEED_MULTIPLIER = 2
    # original 1
    STEP_MULTIPLIER = 1
    # original 1
    DISTANCE_MULTIPLIER = 1
    DIR_MULTIPLIER = 0.5
    ##################################################################

    #### 1 for no reduction when over speed, 0 for no reward when overspeeding ###############
    OVER_SPEED_REWARD = 0.05

    ALLOW_WHEEL_OFF_TRACK = True
    SPEED_DIFF_NO_REWARD = 1.0
    REWARD_PER_STEP_FOR_FASTEST_TIME = 0.1 
    REWARD_FOR_FASTEST_TIME = 800 # should be adapted to track length and other rewards. finish_reward = max(1e-3, (-self.REWARD_FOR_FASTEST_TIME / (15*(self.STANDARD_TIME - self.FASTEST_TIME)))*(steps-self.STANDARD_TIME*15))
    STANDARD_TIME = 11.5  # seconds (time that is easily done by model)
    FASTEST_TIME = 7.5  # seconds (best time of 1st place on the track)

    DEBUG = False

    def __init__(self, verbose=False):
        self.first_racingpoint_index = None
        self.verbose = verbose
        
    def cal_speed_reward(self, optimals, speed, all_wheels_on_track, steps):
        ## no speed reward if one wheel is off track ##
        if self.ALLOW_WHEEL_OFF_TRACK and all_wheels_on_track == False:
            return 0.0

        # Zero reward of obviously too slow
        speed_diff_zero = optimals[2] - speed
        if speed_diff_zero > 0.5 and steps > 3:
            if self.verbose:
                self.state = f"SLOW {speed_diff_zero:.1f} | {self.state}"
            return 0.0

        speed_diff = optimals[2] - speed
        if abs(speed_diff) <= self.SPEED_DIFF_NO_REWARD:
            # we use quadratic punishment (not linear) bc we're not as confident with the optimal speed
            # so, we do not punish small deviations from optimal speed
            speed_reward = (1 - (abs(speed_diff)/(self.SPEED_DIFF_NO_REWARD))**2)**2
        else:
            speed_reward = 0
        
        if speed_diff < 0:
            speed_reward = speed_reward * self.OVER_SPEED_REWARD
            if self.verbose:
                self.state = f"OVER SPEED {speed_diff:.1f} | {self.state}"

        return speed_reward

    def reward_function(self, params):
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

            if abs(track_direction - heading) > 180:
                if track_direction - heading > 0:
                    return direction_diff
                else:
                    return direction_diff * -1
            else:
                if track_direction - heading > 0:
                    return direction_diff * -1
                else:
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


        #################### RACING LINE ######################

        # Optimal racing line
        # Each row: [x,y,speed,timeFromPreviousPoint]
        racing_track = [[2.97715, 0.49328, 2.86653, 0.14799],
            [3.22644, 0.45159, 3.31225, 0.07631],
            [3.48232, 0.42479, 3.92823, 0.06549],
            [3.7822, 0.40778, 4.0, 0.07509],
            [4.18514, 0.40038, 2.22147, 0.18142],
            [4.44306, 0.40474, 2.22147, 0.11612],
            [4.7094, 0.41665, 2.22147, 0.12001],
            [5.06297, 0.44449, 2.22147, 0.15965],
            [5.46464, 0.49347, 2.11293, 0.19151],
            [5.84545, 0.56074, 1.99696, 0.19365],
            [6.07515, 0.64297, 1.83006, 0.13331],
            [6.26037, 0.73566, 1.65864, 0.12487],
            [6.41941, 0.83743, 1.61922, 0.11661],
            [6.55902, 0.94725, 1.45732, 0.12188],
            [6.6808, 1.06517, 1.3, 0.1304],
            [6.78519, 1.19135, 1.3, 0.12598],
            [6.87062, 1.32656, 1.3, 0.12302],
            [6.93381, 1.47171, 1.3, 0.12178],
            [6.97332, 1.62608, 1.3, 0.12257],
            [6.98139, 1.78979, 1.3, 0.12608],
            [6.94445, 1.95906, 1.34582, 0.12874],
            [6.86886, 2.12574, 1.34582, 0.13599],
            [6.74034, 2.2769, 1.66249, 0.11934],
            [6.57654, 2.40698, 1.95592, 0.10694],
            [6.38905, 2.51536, 2.2964, 0.09431],
            [6.18648, 2.60449, 2.84526, 0.07778],
            [5.97543, 2.67958, 3.75897, 0.05959],
            [5.76056, 2.74728, 3.15646, 0.07137],
            [5.56003, 2.81363, 3.15646, 0.06692],
            [5.36074, 2.88362, 3.15646, 0.06692],
            [5.16304, 2.95849, 3.15646, 0.06698],
            [4.96729, 3.03965, 3.15646, 0.06714],
            [4.77392, 3.12898, 3.15646, 0.06748],
            [4.58368, 3.23034, 3.6904, 0.05841],
            [4.39562, 3.34094, 3.94181, 0.05535],
            [4.20893, 3.45779, 3.38485, 0.06507],
            [4.02302, 3.57819, 2.97798, 0.07438],
            [3.8484, 3.69226, 2.56561, 0.0813],
            [3.6828, 3.79721, 2.50339, 0.07832],
            [3.52195, 3.89412, 2.50339, 0.07501],
            [3.36132, 3.98411, 2.50339, 0.07355],
            [3.19849, 4.0665, 2.50339, 0.07289],
            [3.03225, 4.13958, 2.38185, 0.07624],
            [2.86105, 4.2004, 2.13919, 0.08493],
            [2.68406, 4.24832, 1.93875, 0.09458],
            [2.50136, 4.28449, 1.73728, 0.1072],
            [2.31217, 4.30793, 1.52904, 0.12468],
            [2.11511, 4.31642, 1.52904, 0.129],
            [1.90801, 4.30582, 1.52904, 0.13562],
            [1.6867, 4.26648, 1.52904, 0.14701],
            [1.44721, 4.18058, 1.52904, 0.16639],
            [1.20086, 4.01722, 1.52904, 0.19332],
            [1.00648, 3.75075, 1.61583, 0.20413],
            [0.90867, 3.41966, 2.1257, 0.16241],
            [0.8791, 3.09613, 2.49117, 0.13041],
            [0.88996, 2.81283, 2.58325, 0.10975],
            [0.92064, 2.56002, 2.41474, 0.10546],
            [0.96521, 2.3213, 2.27203, 0.10689],
            [1.01882, 2.11134, 2.03959, 0.10624],
            [1.08284, 1.91596, 1.80451, 0.11393],
            [1.15775, 1.73261, 1.80451, 0.10976],
            [1.24395, 1.56082, 1.80451, 0.10651],
            [1.34225, 1.40089, 1.80451, 0.10403],
            [1.45375, 1.25315, 1.80451, 0.10258],
            [1.58206, 1.11927, 1.80451, 0.10276],
            [1.73591, 1.00163, 2.37307, 0.08161],
            [1.90942, 0.89299, 2.62941, 0.07786],
            [2.10429, 0.79194, 2.86653, 0.07658],
            [2.32291, 0.69735, 2.86653, 0.0831],
            [2.56881, 0.6083, 2.86653, 0.09124]]        

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

        self.state = ""

        ############### OPTIMAL X,Y,SPEED,TIME ################

        # Get closest indexes for racing line (and distances to all points on racing line)
        closest_index, second_closest_index = closest_2_racing_points_index(
            racing_track, [x, y])

        # Get optimal [x, y, speed, time] for closest and second closest index
        optimals = racing_track[closest_index]
        optimals_second = racing_track[second_closest_index]

        if self.verbose == True:
          print(f'sp: {speed:.1f} {"=" * math.ceil(speed * 2.5)}{" " * math.floor(10 - speed * 2.5)}', end = ' ')
          _l = max(0, steering_angle / 3)
          print(f'sa: {steering_angle:5.1f} {" " * math.floor(10 - _l)}{"<" * math.ceil(_l)}', end = '|')
          _r = max(0, steering_angle / -3)
          print(f'{">" * math.ceil(_r)}{" " * math.floor(10 - _r)}', end = ' ')
          print(f'x: {x:.1f}, y: {y:.1f}, h: {heading:.1f}, ot: {is_offtrack}, os: {optimals[2]:.2f}, tp: {optimals[3]:.1f}')
        if self.DEBUG == True:
          print(f'dc: {distance_from_center:.2f}, p: {progress:.2f}, st: {steps:3.0f}, cw: {closest_waypoints}, 1c: {closest_index}, 2c: {second_closest_index}, aw: {all_wheels_on_track}, il: {is_left_of_center}, ')
          print(f'tw: {track_width:.2f}')
        
        if is_offtrack == True:
            self.state = f"OFF TRACK | {self.state}"
            if self.verbose == True:
                print(f"r: {1e-3:.3f}")
                print(f"S: {self.state}")
            return float(1e-3)

        # Save first racingpoint of episode for later
        if steps == 1 or self.first_racingpoint_index is None:
            self.first_racingpoint_index = closest_index

        ################ REWARDS ################

        ## Reward if car goes close to optimal racing line ##
        dist = dist_to_racing_line(optimals[0:2], optimals_second[0:2], [x, y])
        distance_reward = max(1e-3, 1 - (dist/(track_width*0.5)))

        ## Reward if speed is close to optimal speed ##
        speed_reward = self.cal_speed_reward(optimals, speed, all_wheels_on_track, steps)

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
            steps_prediction = 0
            reward_prediction = 0

        # Zero reward if obviously wrong direction (e.g. spin)
        direction_diff = racing_direction_diff(
            optimals[0:2], optimals_second[0:2], [x, y], heading)
        if (direction_diff > 0 and steering_angle > 0) or (direction_diff < 0 and steering_angle < 0):
            distance_reward = distance_reward / 2
            speed_reward = 0
            steps_reward = 0
            self.state = f"WRG DIR | {self.state}"
        if abs(direction_diff > 10):
            speed_reward = speed_reward / 3
        dir_reward = min(15, 15 - min(15, abs(direction_diff))) / 15
        # if abs(direction_diff) > 30:
        #     if self.verbose:
        #         self.state = f"WRONG DIRECTION: {direction_diff:.1f} {self.state}"
        #         reward = float(1e-3)
        #         print(f"r: {reward:.3f}")
        #         print(f"S: {self.state}")
        #     return float(1e-3)
            
        ## Incentive for finishing the lap in less steps ##
        if progress == 100:
            finish_reward = max(1e-3, (-self.REWARD_FOR_FASTEST_TIME /
                      (15*(self.STANDARD_TIME - self.FASTEST_TIME)))*(steps-self.STANDARD_TIME*15))
        else:
            finish_reward = 0
        reward = self.BASE_REWARD + distance_reward * self.DISTANCE_MULTIPLIER \
            + finish_reward \
            + speed_reward * self.SPEED_MULTIPLIER \
            + steps_reward * self.STEP_MULTIPLIER \
            + dir_reward * self.DIR_MULTIPLIER

        ####################### VERBOSE #######################
        if self.verbose == True:
            # Closest index, Distance to racing line, Distance reward (w/out multiple), Direction difference
            # Predicted time, Steps reward, Finish reward, Reward
            if self.DEBUG == True:
              print(f"ci: {closest_index}, pt: {projected_time:.1f}, sp: {steps_prediction:.1f}, rp: {reward_prediction:.1f}")
            if finish_reward <= 0:
              print(f"r:{reward:.2f} {'*' * math.ceil(reward*5)}{' ' * math.floor(20-reward*5)}", end =" ")
              print(f"sr:{speed_reward:.1f} {'*' * math.ceil(speed_reward*5)}{' ' * math.floor(10-speed_reward*5)}", end =" ")
              print(f"dr:{distance_reward:.1f} {'*' * math.ceil(distance_reward*10)}{' ' * math.floor(10-distance_reward*10)}", end =" ")
              print(f"di:{dist:.1f} {'*' * math.ceil(dist*100/7)}{' ' * math.floor(10-dist*100/7)}", end =" ")
              print(f"ir:{dir_reward:.1f} {'*' * math.ceil(dir_reward*20)}{' ' * math.floor(10-dir_reward*20)}", end =" ")
              print(f"dd: {direction_diff:5.1f}", end =" ")
              _l = min(max(0, direction_diff / 6), 5)
              print(f'{" " * math.floor(5 - _l)}{"<" * math.ceil(_l)}', end = '|')
              _r = min(max(0, direction_diff / -6), 5)
              print(f'{">" * math.ceil(_r)}{" " * math.floor(5 - _r)}', end = ' ')            
              print(f"tr: {steps_reward:.1f} S: {self.state}")
        return reward

reward_object = Reward() # add parameter verbose=True to get noisy output for testing

def reward_function(params):
    return reward_object.reward_function(params)