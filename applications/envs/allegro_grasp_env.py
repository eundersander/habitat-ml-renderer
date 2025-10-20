# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

from typing import Any

import numpy as np
import numpy.typing as npt
from mochi_gym.core import mochi
from mochi_gym.envs import (
    ActionSpace,
    Info,
    MochiEnv,
    MochiEnvCfg,
    ObservationSpace,
    RewardTerms,
    StructuredAction,
    StructuredObservation,
)
from mochi_gym.utils import mochi_helpers
from mochi_gym.utils.configclasses import configclass

from tbd.utils import mochi_utils

#######################################################################################


@configclass
class AllegroGraspEnvCfg(MochiEnvCfg):
    """Options for the AllegroGraspEnv."""

    # Default environment options
    control_frequency: int = 100
    simulation_frequency: int = 100
    steps_per_episode: int = 1000


#######################################################################################


class AllegroGraspEnv(MochiEnv):

    def __init__(
        self,
        cfg: AllegroGraspEnvCfg | dict[str, Any],
    ):
        """Constructor for the Gym Base environment."""
        if not isinstance(cfg, AllegroGraspEnvCfg):
            cfg = AllegroGraspEnvCfg(**cfg)

        # Initialize the base environment.
        super().__init__(cfg)

        # Initialize the Mochi scene.
        self._init_scene()

        # Get the number of degrees of freedom.
        # These consist of the 6 dofs of the root (3 translation and 3 rotation)
        # plus the joint angles.
        num_dofs = self._agent.get_num_dofs()

        num_controlled_dofs = num_dofs

        # todo: reasonable control limits
        control_limit_scalar = 10.0
        control_limit = (
            np.ones(num_controlled_dofs, dtype=np.float32)
            * control_limit_scalar
        )
        self._setup_action_space(
            control=ActionSpace(
                -control_limit,
                control_limit,
                (num_controlled_dofs,),
                dtype=np.float32,
            ),
        )

        observation_space = {
            "agent_pose": ObservationSpace(
                -np.inf, np.inf, (num_dofs,), dtype=np.float32
            ),
            "object_pose": ObservationSpace(-np.inf, np.inf, (6,), dtype=np.float32),
        }

        self._setup_observation_space(**observation_space)

        # Setup preferred renderer settings.
        if self._renderer:
            self._renderer.set_camera_view(look_from=[-2, 2, 2], look_at=[0, 1, 0])
            self._renderer.set_enable_follow_camera(True)
            self._renderer.set_follow_camera_smoothness(0.8)
            self._renderer.frame_scene()
            self._renderer.add_grid("Floor")


    def _configure_scene_collision(scene):

        # disable collision between environment's links (e.g. cabinets)
        scene.set_contact_type_symmetric(
            "EnvironmentLinks", "EnvironmentLinks", mochi.ContactType.NONE
        )

        scene.set_contact_type_symmetric(
            "Object", "RobotLinks", mochi.ContactType.SYNC
        )

        scene.set_contact_type_symmetric(
            "Object", "EnvironmentLinks", mochi.ContactType.SYNC
        )

        scene.set_contact_type_symmetric(
            "RobotLinks", "EnvironmentLinks", mochi.ContactType.SYNC
        )

    def _init_scene(self):

        def scene_builder():
            # note: do not populate self here

            scene = mochi.create_scene("allegro_grasp")

            from tbd.robots.allegro import create_allegro
            agent = create_allegro(scene)

            mochi_helpers.create_ground_plane(scene)

            mochi_utils.add_prefab("hab_mochi_shared_data/allegro_trajectory_test/allegro_trajectory_test.mochi_prefab", scene)

            AllegroGraspEnv._configure_scene_collision(scene)

            return scene, agent

        self._load_scene(f"allegro_grasp", scene_builder)

        # Perform general environment initialization.
        self._post_init_scene()

        # Get the object actor
        self._object_actor = mochi_helpers.find_actor(self._scene, "allegro_trajectory_test")

        num_dofs = self._agent.get_num_dofs()
        self._initial_pose = np.array([0.0] * num_dofs)
        self._initial_velocity = mochi_helpers.get_articulated_joint_velocities(
            self._agent
        )

    def _reset_scene(self):
        super()._reset_scene()

    ####################################################################################
    # Functions handling environment initialization and resetting.
    ####################################################################################

    def _apply_action(self, action: StructuredAction):

        target_pose = action["control"]

        # Set the target pose to the new target pose
        self._agent.set_articulated_target_pose(target_pose)

    def _make_observation(self) -> tuple[StructuredObservation, Info]:
        # Construct the pose observation.
        agent_pose = mochi_helpers.get_articulated_pose(self._agent)

        object_pose = \
            mochi_helpers.TransformRT_to_numpy(
                self._object_actor.get_center_of_mass_transform()
            )

        # Fill in the observation and info.
        obs = {
            "agent_pose": agent_pose,
            "object_pose": object_pose,
        }

        info = {
            "agent_root_com_x": agent_pose[0],
            "agent_root_com_y": agent_pose[1],
            "agent_root_com_z": agent_pose[2],
            "object_pos_x": object_pose[0][0],
            "object_pos_y": object_pose[0][1],
            "object_pos_z": object_pose[0][2],
            "object_rot_x": object_pose[1][0],
            "object_rot_y": object_pose[1][1],
            "object_rot_z": object_pose[1][2],
        }
        return obs, info

    def _compute_reward_terms(
        self, action: StructuredAction, observation: StructuredObservation, info: Info
    ) -> RewardTerms:
        
        return {
            "dummy": 0.0,
        }

