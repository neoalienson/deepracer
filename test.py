#from reward_function import reward_function
from reward_function import Reward
import unittest
import math

class TestRewardFunction(unittest.TestCase):
  waypoints = [[2.8873885499889385, 0.726467741007691], [3.1675912209711705, 0.704786488311369], [3.4551731738475713, 0.6921786257120108], [3.7532515756822287, 0.6858100463187193], [4.072814338243193, 0.6836081931173711], [4.500002230529587, 0.6837609167129147], [4.549995073956144, 0.6837787896136626], [5.117381147897781, 0.6908041075226552], [5.447982562982464, 0.7112322029646044], [5.711265580422473, 0.7422346953355425], [5.941372105449603, 0.7849646168697144], [6.14912709690292, 0.8407803487746184], [6.336758932063642, 0.910667356962588], [6.503516690922521, 0.9948399398813299], [6.647625884029711, 1.0933636666158342], [6.767148492564518, 1.2064015782188044], [6.857904170606057, 1.3350866866561408], [6.921937617475411, 1.4764660946579922], [6.960268235163922, 1.6279734619836947], [6.9668995801856575, 1.7888071991434118], [6.929767421700819, 1.9551543405695744], [6.853796172049812, 2.119102709675103], [6.7269327251774005, 2.268416334375874], [6.565827306421308, 2.3979064968172388], [6.380755123221848, 2.5063265223251174], [6.180371705554723, 2.5960264990184765], [5.97126498649426, 2.6720718677404474], [5.75829177463112, 2.741103010083892], [5.558411769338754, 2.810132384390418], [5.360049465761351, 2.88360578275889], [5.163331306801121, 2.962188029071304], [4.968449030193712, 3.0468263416666996], [4.775520319459698, 3.138325431489057], [4.584624396203516, 3.237452798325894], [4.395624809243852, 3.344197010326614], [4.208250346496813, 3.4578934289044962], [4.022165217846894, 3.577403746276934], [3.8371280683829303, 3.7018419231567705], [3.681861411012094, 3.809703887563246], [3.5252922717094037, 3.9117983675963584], [3.3667407341899676, 4.006064126580926], [3.2053248589385617, 4.090414741034139], [3.0401251953842676, 4.163356432852998], [2.8702442130275108, 4.22393077448964], [2.6948633514524545, 4.271622788605077], [2.5131932089848545, 4.306023645894755], [2.324525679916916, 4.326723820809339], [2.1269630912619206, 4.330802975266311], [1.9181050793836385, 4.3138121184730105], [1.6947191320004, 4.267408676972845], [1.4541627337365117, 4.174008490919465], [1.2111900454555669, 4.006532228942984], [1.0192295285380961, 3.744022018008346], [0.9222054925325214, 3.4205054375538393], [0.8892660439411404, 3.1044388864862364], [0.896007467184927, 2.8207603596691184], [0.9240494312211823, 2.5628118514410283], [0.9660525314669286, 2.324603051064647], [1.0180283266844032, 2.1122854381532052], [1.08079016698792, 1.915129811182102], [1.1551369760045151, 1.7310757057890727], [1.2416231723876427, 1.5601480656474387], [1.341129981140405, 1.4032388427610951], [1.4547258930465157, 1.2610931996668353], [1.5865309544578126, 1.1364118322222136], [1.7447260773737912, 1.0322868812760757], [1.9265552947643938, 0.9430548066740163], [2.1328222834811292, 0.8677942536468937], [2.3641125208150084, 0.8067988687678815], [2.617512764005648, 0.759921447767141]],
  raceline_point = [3.0, 1.0, 2.0, 0.0]
  steps = 5

  def setUp(self):
     self.params = {
     'all_wheels_on_track': True,
     'x': 3.2000,
     'y': 0.6831,
     'distance_from_center': 0.0,
     'is_left_of_center': True,
     'heading': 0.1910,
     'progress': 0.7920,
     'steps': 1.0,
     'speed': 1.63,
     'steering_angle': -8.57,
     'track_width':  0.76,
     'waypoints': self.waypoints,
     'closest_waypoints': [0, 1],
     'is_offtrack': False
     }
     self.ro = Reward()
     
  def test_rt_issue_1(self):
    self.ro.verbose = True
    self.params = {
     'all_wheels_on_track': True,
     'x': 2.5,
     'y': 5.0,
     'distance_from_center': 0.05,
     'is_left_of_center': False,
     'heading': 127.0,
     'progress': 5.87,
     'steps': 14,
     'speed': 2.21,
     'steering_angle': -13.2,
     'track_width':  0.76,
     'waypoints': self.waypoints,
     'closest_waypoints': [73, 74],
     'is_offtrack': False
    }
    r = self.ro.reward_function(self.params)
    print(f'r*: {r}')
    self.assertEqual(math.ceil(r * 1000), 2)

  # prevent breaking code from verbose 
  def test_verbose(self):
    self.ro.verbose = True
    self.ro.DEBUG = True
    self.assertTrue(self.ro.reward_function(self.params))

  def test_offtrack(self):
    self.params['is_offtrack']= True
    self.assertEqual(self.ro.reward_function(self.params), 1e-3)

  def test_all_wheels_on_track(self):
    self.params['all_wheels_on_track']= False
    self.assertEqual(math.ceil(self.ro.reward_function(self.params) * 1000), 589)

  def test_slow_after_reset(self):
    self.params['speed']= 0.0
    self.assertEqual(math.ceil(self.ro.reward_function(self.params) * 1000), 589)

  def test_slow_after_4_steps(self):
    self.params['speed']= 0.0
    self.params['steps']= 4
    self.assertEqual(math.ceil(self.ro.reward_function(self.params) * 1000), 589)

  def test_speed_reward(self):
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 2, True, self.steps), 1)  

  def test_slow_speed_reward(self):
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 0.8, True, self.steps), 0)
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 1.5, True, self.steps), 0.5625)
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 1.6, True, self.steps)* 1000), 706)    

  def test_speed_reward_on_wheel_off_track(self):
    self.ro.ALLOW_WHEEL_OFF_TRACK = True
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 2.0, True, self.steps), 1.0)
    self.ro.ALLOW_WHEEL_OFF_TRACK = True
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 2.0, False, self.steps), 0.0)

  def test_over_speed_no_reward(self):
    self.ro.OVER_SPEED_REWARD = 0
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 2.1, True, self.steps), 0.0)
    self.assertEqual(self.ro.cal_speed_reward(self.raceline_point, 3.0, True, self.steps), 0.0)

  def test_over_speed_reward(self):
    self.ro.OVER_SPEED_REWARD = 0.5
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 2.1, True, self.steps) * 1000), 491)
    self.ro.OVER_SPEED_REWARD = 1
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 2.1, True, self.steps) * 1000), 981)
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 2.5, True, self.steps) * 1000), 563)
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 2.8, True, self.steps) * 1000), 130)
    self.assertEqual(math.ceil(self.ro.cal_speed_reward(self.raceline_point, 3.0, True, self.steps) * 1000), 0)

if __name__ == '__main__':
    unittest.main()