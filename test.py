from reward_function import *
import unittest
import math


class TestRewardFunc(unittest.TestCase):
  waypoints = [[2.8873885499889385, 0.726467741007691], [3.1675912209711705, 0.704786488311369], [3.4551731738475713, 0.6921786257120108], [3.7532515756822287, 0.6858100463187193], [4.072814338243193, 0.6836081931173711], [4.500002230529587, 0.6837609167129147], [4.549995073956144, 0.6837787896136626], [5.117381147897781, 0.6908041075226552], [5.447982562982464, 0.7112322029646044], [5.711265580422473, 0.7422346953355425], [5.941372105449603, 0.7849646168697144], [6.14912709690292, 0.8407803487746184], [6.336758932063642, 0.910667356962588], [6.503516690922521, 0.9948399398813299], [6.647625884029711, 1.0933636666158342], [6.767148492564518, 1.2064015782188044], [6.857904170606057, 1.3350866866561408], [6.921937617475411, 1.4764660946579922], [6.960268235163922, 1.6279734619836947], [6.9668995801856575, 1.7888071991434118], [6.929767421700819, 1.9551543405695744], [6.853796172049812, 2.119102709675103], [6.7269327251774005, 2.268416334375874], [6.565827306421308, 2.3979064968172388], [6.380755123221848, 2.5063265223251174], [6.180371705554723, 2.5960264990184765], [5.97126498649426, 2.6720718677404474], [5.75829177463112, 2.741103010083892], [5.558411769338754, 2.810132384390418], [5.360049465761351, 2.88360578275889], [5.163331306801121, 2.962188029071304], [4.968449030193712, 3.0468263416666996], [4.775520319459698, 3.138325431489057], [4.584624396203516, 3.237452798325894], [4.395624809243852, 3.344197010326614], [4.208250346496813, 3.4578934289044962], [4.022165217846894, 3.577403746276934], [3.8371280683829303, 3.7018419231567705], [3.681861411012094, 3.809703887563246], [3.5252922717094037, 3.9117983675963584], [3.3667407341899676, 4.006064126580926], [3.2053248589385617, 4.090414741034139], [3.0401251953842676, 4.163356432852998], [2.8702442130275108, 4.22393077448964], [2.6948633514524545, 4.271622788605077], [2.5131932089848545, 4.306023645894755], [2.324525679916916, 4.326723820809339], [2.1269630912619206, 4.330802975266311], [1.9181050793836385, 4.3138121184730105], [1.6947191320004, 4.267408676972845], [1.4541627337365117, 4.174008490919465], [1.2111900454555669, 4.006532228942984], [1.0192295285380961, 3.744022018008346], [0.9222054925325214, 3.4205054375538393], [0.8892660439411404, 3.1044388864862364], [0.896007467184927, 2.8207603596691184], [0.9240494312211823, 2.5628118514410283], [0.9660525314669286, 2.324603051064647], [1.0180283266844032, 2.1122854381532052], [1.08079016698792, 1.915129811182102], [1.1551369760045151, 1.7310757057890727], [1.2416231723876427, 1.5601480656474387], [1.341129981140405, 1.4032388427610951], [1.4547258930465157, 1.2610931996668353], [1.5865309544578126, 1.1364118322222136], [1.7447260773737912, 1.0322868812760757], [1.9265552947643938, 0.9430548066740163], [2.1328222834811292, 0.8677942536468937], [2.3641125208150084, 0.8067988687678815], [2.617512764005648, 0.759921447767141]], 

  def setUp(self):
    SETTINGS.verbose = False
    # SETTINGS.debug = True
    SETTINGS.STAGE = 1
    self.params = {
     'all_wheels_on_track': True,
     'x': 3.2000,
     'y': 0.60513,
     'distance_from_center': 0.0,
     'is_left_of_center': True,
     'heading': 0,
     'progress': 0.7920,
     'steps': 1.0,
     'speed': 2.2,
     'steering_angle': -8.57,
     'track_width':  0.76,
     'waypoints': self.waypoints,
     'closest_waypoints': [0, 1],
     'is_offtrack': False
    }
    init_state()

  def test_direction_difference_exceed_30(self):
    self.params = {'all_wheels_on_track':False,'x':0.1402956865016356,'y':4.045675685819531,'distance_from_center':0.6306292205255717,'is_left_of_center':False,'heading':-154.9588545914767,'progress':7.9108419101282745,'steps':20.0,'speed':3.0,'steering_angle':-11.3,'track_width':0.7593030450788312,'waypoints':self.waypoints ,'closest_waypoints':[86, 87],'is_offtrack':True}
    reward_function(self.params)
    self.assertEqual(REWARDS.immediate, 1e-3)
 

  def test_direction_difference_less_30(self):
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)
    self.params['heading'] = self.params['heading'] - 30
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)

  # The speed of the car is 1.5 m/s slower than its optimal speed on a straight section. Essentially the car is going too slow on straight sections.
  def test_too_slow_beyond_stage_3(self):
    SETTINGS.STAGE = 3
    self.params['speed'] = 0.1
    reward_function(self.params)
    self.assertEqual(REWARDS.immediate, 1e-3)

  def test_no_too_slow_in_stage_1(self):
    self.params['speed'] = 0.1
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)

  # any speed going beyond a safe learning value consider as too fast in stage1
  # def test_too_fast_in_stage_1(self):
  #   self.params['speed'] = 2.4
  #   reward_function(self.params)
  #   self.assertEqual(REWARDS.immediate, 1e-3)

  def test_no_too_fast_in_right_turn_section(self):
    self.params['speed'] = 4
    self.params['heading'] = 43.1
    self.params['closest_waypoints'] = [26, 27]
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)
    SETTINGS.STAGE = 2
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)

  # The car’s speed is at least 1 m/s greater than its optimal speed while it is making a turn. Essentially the car is turning too fast.
  def test_too_fast(self):
    self.params['speed'] = 5.1
    reward_function(self.params)
    self.assertEqual(REWARDS.immediate, 1e-3)

  def test_close_to_optimal_speed(self):
    SETTINGS.STAGE = 2
    self.params['speed'] = 4.1
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)

  def test_correct_direction(self):
    self.params['heading'] = self.params['heading'] - 10
    reward_function(self.params)
    self.assertNotEqual(REWARDS.immediate, 1e-3)

  def test_keep_all_wheels_on_track(self):
    self.params['all_wheels_on_track'] = False
    self.assertEqual(reward_function(self.params), 0.001)

  def test_can_make_turn_or_go_straight_in_straight_section(self):
    self.params['closest_waypoints'] = [47, 48]
    self.params['heading'] = 112.1
    for steering_angle in [-10, 0, 10]:
      self.params['steering_angle'] = steering_angle
      reward_function(self.params)
      self.assertNotEqual(REWARDS.immediate, 1e-3)

  def test_can_make_right_turn_or_go_straight_in_right_turn_section(self):
    self.params['closest_waypoints'] = [26, 27]
    self.params['heading'] = 43
    for steering_angle in [-10, 0]:
      self.params['steering_angle'] = steering_angle
      reward_function(self.params)
      self.assertNotEqual(REWARDS.immediate, 1e-3)

  def test_should_not_make_left_turn_in_right_turn_section(self):
    self.params['closest_waypoints'] = [26, 27]
    self.params['steering_angle'] = 10
    reward_function(self.params)
    self.assertEqual(REWARDS.immediate, 1e-3)

  def test_can_make_left_turn_go_straight_in_left_turn_section(self):
    self.params['closest_waypoints'] = [19, 20]
    for steering_angle in [0, 10]:
      self.params['steering_angle'] = steering_angle
      reward_function(self.params)
      self.assertNotEqual(REWARDS.immediate, 1e-3)

  def test_should_not_make_right_turn_in_left_turn_section(self):
    self.params['closest_waypoints'] = [19, 20]
    self.params['steering_angle'] = -10
    reward_function(self.params)
    self.assertEqual(REWARDS.immediate, 1e-3)

  def test_is_not_right_turn_section(self):
    self.params['closest_waypoints'] = [0, 1]
    reward_function(self.params)
    self.assertFalse(is_right_turn_section())

  def test_is_not_left_turn_section(self):
    for waypoint in [[0, 1], [28, 29], [47, 48], [55, 56], [68, 69]]:
      self.params['closest_waypoints'] = waypoint
      reward_function(self.params)
      self.assertFalse(is_left_turn_section())

  def test_is_left_turn_section(self):
    for waypoint in [[19, 20], [41, 42], [51, 52], [62, 63]]:
      self.params['closest_waypoints'] = waypoint
      reward_function(self.params)
      self.assertTrue(is_left_turn_section())

  def test_is_right_turn_section(self):
    self.params['closest_waypoints'] = [26, 27]
    reward_function(self.params)
    self.assertTrue(is_right_turn_section())

  def test_is_not_straight_section(self):
    self.params['closest_waypoints'] = [26, 27]
    reward_function(self.params)
    self.assertFalse(is_straight_section())

  def test_is_straight_section(self):
    for waypoint in [[0, 1], [69, 69], [57, 58]]:
      self.params['closest_waypoints'] = waypoint
      reward_function(self.params)
      self.assertTrue(is_straight_section())

  def test_off_track(self):
    self.params['is_offtrack'] = True
    self.assertEqual(reward_function(self.params), 0.001)

  def test_state(self):
    self.assertEqual(STATE.prev_speed, None)
    reward_function(self.params)
    self.assertNotEqual(STATE.prev_speed, None)

  @unittest.SkipTest
  def test_verbose(self):
    SETTINGS.verbose = True
    reward_function(self.params)

  # @unittest.SkipTest
  def test_debug(self):
    SETTINGS.verbose = True
    SETTINGS.debug = True
    reward_function(self.params)

  def test_distance_reward(self):
    reward_function(self.params)
    self.assertTrue(get_distance_reward() > 0.9)
    self.params['y'] = 1
    reward_function(self.params)
    self.assertEqual(get_distance_reward(), 1e-3)

if __name__ == '__main__':
    unittest.main()