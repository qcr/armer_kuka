"""
ABBROSRobot module defines the ABBROSRobot type
ABBROSRobot provides robot-specific callbacks for recovery and setting impedance.
.. codeauthor:: Gavin Suddreys
.. codeauthor:: Dasun Gunasinghe
"""
import rospy
import actionlib
import roboticstoolbox as rtb

from armer.robots import ROSRobot

from std_srvs.srv import EmptyRequest, EmptyResponse
from std_srvs.srv import Trigger, TriggerRequest

from armer_msgs.msg import ManipulatorState

from armer_msgs.srv import \
    SetCartesianImpedanceRequest, \
    SetCartesianImpedanceResponse

# Service type from abb_robot_controller
from abb_robot_msgs.srv import TriggerWithResultCode, TriggerWithResultCodeRequest
from abb_robot_msgs.msg  import SystemState

class ABBROSRobot(ROSRobot):
    def __init__(self,
                 robot: rtb.robot.Robot,
                 controller_name: str = None,
                 recover_on_estop: bool = True,
                 *args,
                 **kwargs):

        super().__init__(robot, *args, **kwargs)
        self.controller_name = controller_name \
            if controller_name else self.joint_velocity_topic.split('/')[1]

        self.recover_on_estop = recover_on_estop
        self.last_estop_state = 0

        self.robot_state = None
        self.safety_state = None     

        """
        -> DG: [26/08/21] the addition of ABB specific services for starting
                and communicating with the ABB Real Robot. Three specific
                calls:
                1) pp_to_main - sets the robot controller program pointer to main
                2) start_rapid - begins EGM motion on the robot controller
                3) stop_rapid - stops the EGM motion on the robot controller
        """
        self.pp_to_main = rospy.ServiceProxy('/rws/pp_to_main', TriggerWithResultCode)
        self.pp_to_main.wait_for_service()

        self.start_rapid = rospy.ServiceProxy('/rws/start_rapid', TriggerWithResultCode)
        self.start_rapid.wait_for_service()

        self.stop_rapid = rospy.ServiceProxy('/rws/stop_rapid', TriggerWithResultCode)
        self.stop_rapid.wait_for_service()

        self.abb_state_sub = rospy.Subscriber('/rws/system_states', SystemState, self.abb_state_cb)
        
        # Stop/Start-Up/Recovery Callback
        self.recover_cb(EmptyRequest())

    def recover_cb(self, req: EmptyRequest) -> EmptyResponse: # pylint: disable=no-self-use
        """[summary]
            ROS Service callback:
            Invoke any available error recovery functions on the robot when an error occurs
            :param req: an empty request
            :type req: EmptyRequest
            :return: an empty response
            :rtype: EmptyResponse
        """
        # Stop rapid -> run regardless to ensure controller is in stopped state
        print('Armer_ABB: stop_rapid Execution...')
        self.stop_rapid(TriggerWithResultCodeRequest())

        # Arbitrary sleep period - default 1 sec
        rospy.sleep(1)

        # Reset program pointer to main in controller software
        print('Armer_ABB: pp_to_main Execution...')
        self.pp_to_main(TriggerWithResultCodeRequest())
        
        # Arbitrary sleep period - default 1 sec
        rospy.sleep(1)

        print('Armer_ABB: start_rapid Execution...')
        self.start_rapid(TriggerWithResultCodeRequest())

        return EmptyResponse()

    
    def get_state(self):
        state = super().get_state()

        if self.robot_state:
            state.errors |= ManipulatorState.LOCKED if not self.robot_state.motors_on else 0
            
        if self.robot_state and self.robot_state.motors_on:
            if self.recover_on_estop and self.last_estop_state == 1:
                self.recover_cb(EmptyRequest())

        self.last_estop_state = 1 if not self.robot_state.motors_on else 0

        return state

    def abb_state_cb(self, msg):
        self.robot_state = msg