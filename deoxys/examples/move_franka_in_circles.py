from deoxys.franka_interface import FrankaInterface
from deoxys.utils.config_utils import get_default_controller_config
from deoxys.experimental.motion_utils import reset_joints_to
from deoxys.utils import transform_utils
from deoxys.utils.log_utils import get_deoxys_example_logger

import argparse
import numpy as np

logger = get_deoxys_example_logger()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface-cfg", type=str, default="charmander.yml")
    parser.add_argument("--controller-type", type=str, default="OSC_POSE")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    # This code will move in circles by using velocity control
    robot_interface = FrankaInterface(
        'config/charmander.yml', use_visualizer=False
    )

    # controller_type = 'OCS_POSE'
    controller_type = args.controller_type
    controller_cfg = get_default_controller_config(controller_type)

    # First reset
    reset_joint_positions = [
        0.09162008114028396,
        -0.19826458111314524,
        -0.01990020486871322,
        -2.4732269941140346,
        -0.01307073642274261,
        2.30396583422025,
        0.8480939705504309,
    ]

    reset_joints_to(robot_interface, reset_joint_positions)

    pose_changes = [
        [0.5, 0.5, 0.0],
        [0.0, 0.5, 0.5],
        [0.0, 0.0, 0.5],
        [0.0, -0.5, 0.0],
        [0.0, 0.0, -0.5],
        [-0.5, 0.0, 0.0]
    ]
    for i in range(6):
        delta_pos = pose_changes[i]

        # Get target pose 
        current_pose = robot_interface.last_eef_pose
        current_pos = current_pose[:3, 3:]
        current_rot = current_pose[:3, :3]
        target_pos = np.array(delta_pos).reshape(3,1) + current_pos
        print('current_pos: {}'.format(current_pos))
        
        # Get target quat
        current_quat = transform_utils.mat2quat(current_rot)
        target_quat = current_quat # Should add if needed

        for _ in range(16):
            current_pose = robot_interface.last_eef_pose
            current_pos = current_pose[:3, 3:]
            current_rot = current_pose[:3, :3]

            # Get the translational action
            action_pos = (target_pos - current_pos).flatten() # Adding the difference only
            action_pos = np.clip(action_pos, -1.0, 1.0)

            # Get the rotational action            
            current_quat = transform_utils.mat2quat(current_rot)
            quat_diff = transform_utils.quat_distance(target_quat, current_quat)
            action_axis_angle = transform_utils.quat2axisangle(quat_diff)
            action_axis_angle = np.clip(action_axis_angle, -0.5, 0.5)

            # Merge the two action
            action = action_pos.tolist() + np.zeros(3).tolist() + [-1.0]
            logger.info(f'Action to apply: Pose: {action_pos}, Rotation: {action_axis_angle}')

            robot_interface.control(
                controller_type=controller_type,
                action=action,
                controller_cfg=controller_cfg,
            )
    
    robot_interface.close()

if __name__ == '__main__':
    main()

    # for i in range()

    # move_to_target_pose(
    #     robot_interface,
    #     controller_type,
    #     controller_cfg,
    #     target_delta_pose=[0.2, 0.0, 0.0, 0.0, 0.5, 0.2],
    #     num_steps=80,
    #     num_additional_steps=40,
    #     interpolation_method="linear",
    # )


