# (c) Meta Platforms, Inc. and affiliates. Confidential and proprietary.

from typing import Any, Type

import numpy as np

from mochi_gym.envs import MochiEnv
from mochi_gym.utils.vector import HybridVectorEnv

from allegro_grasp_env import AllegroGraspEnv

########################################################################################


def run_with_gymnasium_vectorization(
    cls: Type[MochiEnv],
    cfg: dict[str, Any],
    num_environments: int,
    num_environments_per_worker: int,
    num_steps: int,
):
    """
    Copied from Mochi mochi_gym/apps/envs/run_with_gymnasium_vectorization.py
    """

    assert issubclass(cls, MochiEnv), "The given class must inherit MochiEnv"

    # Generate hybrid (async + sync) vectorized environment. This creates multiple
    # async worker processes, where each worker runs a SyncVectorEnv with multiple
    # environments.
    env_creators = [lambda: cls(cfg) for _ in range(num_environments)]
    env = HybridVectorEnv(env_creators, num_envs_per_worker=num_environments_per_worker)
    print(f"Created HybridVectorEnv with {num_environments} environments.")
    print(
        f"Running {env.num_workers} async workers, with {env.num_envs_per_worker} "
        "environments per worker."
    )
    print("Observation space shape:", env.flat_observation_space.shape)
    print("Action space shape:", env.flat_action_space.shape)

    # Perform first reset. Here we can provide a global reset seed for all environments,
    # or a list of reset seeds for each environment. See the documentation for more
    # details regarding how the observations and info dictionaries are packed.
    # https://gymnasium.farama.org/api/vector/#gymnasium.vector.VectorEnv
    #
    # IMPORTANT: HybridVectorEnv does not support reset masks. If you need to force
    # reset specific environments, use Gymnasium's AsyncVectorEnv or SyncVectorEnv
    # directly.
    reset_seeds = list(range(num_environments))
    _, infos = env.reset(seed=reset_seeds)

    # Run the environment for some steps.
    returns = np.zeros(num_environments)
    for step in range(num_steps):
        # Sample random action and step using the flattened action space.
        # NOTE: No need to call env.reset() here for terminated/truncated environments,
        # the HybridVectorEnv will automatically reset them. See
        # https://farama.org/Vector-Autoreset-Mode for details on autoreset modes.
        action = env.flat_action_space.sample()
        _, rewards, terminateds, truncateds, infos = env.step(action)
        returns += rewards

        # Report progress.
        for i, (ret, term, trun) in enumerate(zip(returns, terminateds, truncateds)):
            if term or trun:
                wat = "terminated" if term else "truncated"
                why = infos[f"{wat}_reason"][i]
                print(f"Environment {i} {wat} at step {step} with return {ret}: {why}.")
                returns[i] = 0.0

    # Close the environment.
    env.close()
    del env

    # Print the final returns.
    for i, ret in enumerate(returns):
        print(f"Environment {i} finished with return {ret}.")
    print()


########################################################################################

if __name__ == "__main__":
    run_with_gymnasium_vectorization(
        cls=AllegroGraspEnv,
        cfg={"render_mode": None},
        num_environments=2,
        num_environments_per_worker=2,
        num_steps=200,
    )
