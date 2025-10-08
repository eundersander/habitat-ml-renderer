# Copyright (c) Meta Platforms, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import mochi
from mochi_gym.utils import mochi_helpers

from tbd.utils import mochi_utils

# todo: delete
def get_allegro_joint_to_dof_index_map():
    dof_map = {
        # base has 6 dofs
        "base_tx": 0,
        "base_ty": 1,
        "base_tz": 2,
        "base_rx": 3,
        "base_ry": 4,
        "base_rz": 5,
        # finger joints
        "joint_12.0": 6,
        "joint_8.0": 7,
        "joint_4.0": 8,
        "joint_0.0": 9,
        "joint_13.0": 10,
        "joint_9.0": 11,
        "joint_5.0": 12,
        "joint_1.0": 13,
        "joint_14.0": 14,
        "joint_10.0": 15,
        "joint_6.0": 16,
        "joint_2.0": 17,
        "joint_15.0": 18,
        "joint_11.0": 19,
        "joint_7.0": 20,
        "joint_3.0": 21,
        # fixed joints don't have dofs
        # "joint_15.0_digit2_sensor_base_tip": 22,
        # "joint_15.0_digit2_sensor_base": 23,
        # "joint_11.0_digit2_sensor_base_tip": 24,
        # "joint_11.0_digit2_sensor_base": 25,
        # "joint_7.0_digit2_sensor_base_tip": 26,
        # "joint_7.0_digit2_sensor_base": 27,
        # "joint_3.0_digit2_sensor_base_tip": 28,
        # "joint_3.0_digit2_sensor_base": 29
    }
    return dof_map


def create_allegro(scene):
    return Allegro(scene).get_robot_actor()

class Allegro:
    def __init__(self, mochi_scene):

        self._actor = None  # todo
        self._mochi_scene = mochi_scene

        self._add_prefab_to_scene()

        self._add_robot_controller()

        self._configure_robot_self_collision()

    def _add_robot_controller(self):
        hab_robot = self._actor

        num_links = 25

        null_tracking = mochi.PoseTrackingParams()
        joint_tracking = mochi.DynamicArrayPoseTrackingParams(
            [null_tracking] * num_links
        )
        link_rot_tracking = mochi.DynamicArrayPoseTrackingParams(
            [null_tracking] * num_links
        )
        link_pos_tracking = mochi.DynamicArrayPoseTrackingParams(
            [null_tracking] * num_links
        )

        armjoint_tracking = mochi.PoseTrackingParams()
        armjoint_tracking.stiffness = 4e5
        armjoint_tracking.damping = 4e4

        handjoint_tracking = mochi.PoseTrackingParams()
        handjoint_tracking.stiffness = 2e1
        handjoint_tracking.damping = 2e0

        # 1e1, 1e0 too low, can't lift hand
        base_pos_tracking = mochi.PoseTrackingParams()
        base_pos_tracking.stiffness = 1e6
        base_pos_tracking.damping = 1e5

        # 1e1, 1e0 works
        base_rot_tracking = mochi.PoseTrackingParams()
        base_rot_tracking.stiffness = 1e6
        base_rot_tracking.damping = 1e5

        for i in range(num_links):
            if i == 0:
                link_pos_tracking[i] = base_pos_tracking
                link_rot_tracking[i] = base_rot_tracking
            else:
                joint_tracking[i] = handjoint_tracking

        controller_params = mochi.CreatePoseControllerParams()
        controller_params.joint_tracking = joint_tracking
        controller_params.link_pos_tracking = link_pos_tracking
        controller_params.link_rot_tracking = link_rot_tracking

        hab_robot.add_articulated_pose_controller(controller_params)

    def _add_prefab_to_scene(self):

        mochi_utils.add_prefab("hab_mochi_shared_data/allegro/allegro.mochi_prefab", self._mochi_scene)

        self._actor = mochi_helpers.find_actor(self._mochi_scene, "allegro")

    def _configure_robot_self_collision(self):
        scene = self._mochi_scene
        robot_link_actors_by_name = {}
        hab_robot = self.get_robot_actor()
        for link_handle in hab_robot.get_nested_link_actors():
            link_actor = scene.get_actor(link_handle)
            robot_link_actors_by_name[link_actor.get_name()] = link_actor

        if True:
            # disable all self-collision for now
            scene.set_contact_type_symmetric(
                "RobotLinks", "RobotLinks", mochi.ContactType.NONE
            )
        else:
            scene.set_contact_type_symmetric(
                "RobotLinks", "RobotLinks", mochi.ContactType.SYNC
            )

            # disable certain self-collisions that are otherwise always present due to how
            # allegro is authored. Note that collision between parent and child
            # links is always disabled by default so those pairs don't need to be included here.
            disable_robot_self_collision_link_pairs = [
                ("link_3.0_digit2_sensor_base", "link_3.0_tip"),
                ("link_7.0_digit2_sensor_base", "link_7.0_tip"),
                ("link_11.0_digit2_sensor_base", "link_11.0_tip"),
                ("link_15.0_digit2_sensor_base", "link_15.0_tip"),
            ]
            for pair in disable_robot_self_collision_link_pairs:
                handles = tuple(
                    robot_link_actors_by_name[f"{robot_actor_name}/{name}"].get_handle()
                    for name in pair
                )
                scene.allow_contact(handles[0], handles[1], allow=False)
                scene.allow_contact(handles[1], handles[0], allow=False)

    def get_robot_actor(self):

        return self._actor

    # todo: move to separate util
    def register_contact_points_query(self):
        scene = self._mochi_scene
        self._robot_collidable_link_actors = []
        hab_robot = self.get_robot_actor()
        for link_handle in hab_robot.get_nested_link_actors():
            link_actor = scene.get_actor(link_handle)
            if not link_actor.has_mesh():
                continue
            link_actor.register_query(mochi.QueryType.CONTACT_POINTS)
            self._robot_collidable_link_actors.append(link_actor)

    # todo: move to sample code
    def process_robot_contact_points(self):
        """
        Reference code for processing contact points.
        """
        if not hasattr(self, "_robot_collidable_link_actors"):
            raise RuntimeError(
                "You must call register_robot_contact_points_query before calling process_robot_contact_points."
            )
        num_contact_points = 0
        for link_actor in self._robot_collidable_link_actors:
            link_contact_points = link_actor.get_contact_points_world_space()
            if len(link_contact_points):
                print(
                    f"link {link_actor.get_name()} {len(link_contact_points)} contacts"
                )
            num_contact_points += len(link_contact_points)
        if num_contact_points == 0:
            print("no contacts")

