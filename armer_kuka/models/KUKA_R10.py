#!/usr/bin/env python

import numpy as np
from pathlib import PurePosixPath
from roboticstoolbox.robot.ERobot import ERobot
from roboticstoolbox.tools import xacro
from roboticstoolbox.tools import URDF
from roboticstoolbox.tools import data
from spatialmath import SE3
from rospkg import RosPack

class KUKA_R10(ERobot):

    def __init__(self):
        old_base = data.base_path
        data.set_base_path(RosPack().get_path('armer_kuka') + '/data')
        
        #links, name, _, _ = self.URDF_read(
        links, name = self.URDF_read("robots/kr10r900_2.xacro")

        data.set_base_path(old_base)
                
        super().__init__(
            links, name=name, manufacturer="KUKA", gripper_links=links[7]
        )
        
        self.addconfiguration(
            "qr", np.array([0, 0, 0, 0, 0, 0])
        )

if __name__ == "__main__":  # pragma nocover

    robot = KUKA_R10()
    print(robot)