"""
#   Environment Communication Structure
#    - Father class that creates the structure to communicate with multples setups of enviroment
#    - To create your wrapper from env to communcation, use inherit from this class! 
"""


import time
from typing import Dict, List, Optional

import gymnasium as gym
import numpy as np
from rsoccer_gym.Entities import Frame, Robot
from rsoccer_gym.Simulators.rsim import RSimVSS
from rsoccer_gym.Simulators.fira import Fira


class VSSBaseEnv(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"],
    }
    NORM_BOUNDS = 1.2
    MAX_EPISODE_STEPS = 1200

    def __init__(
        self,
        field_type: int,
        n_robots_blue: int,
        n_robots_yellow: int,
        time_step: float,
        use_fira: bool = False,
        render_mode = None
    ):
        # Initialize Simulator
        self.time_step = time_step

        if not use_fira:
            self.rsim = RSimVSS(
                field_type=field_type,
                n_robots_blue=n_robots_blue,
                n_robots_yellow=n_robots_yellow,
                time_step_ms=int(self.time_step * 1000),
            )
        elif field_type == 0:
            self.rsim = Fira()
        else:
            raise ValueError("rsoccer fira wrapper only supports field type 0")
        self.n_robots_blue = n_robots_blue
        self.n_robots_yellow = n_robots_yellow

        # Get field dimensions
        self.field_type = field_type
        self.field = self.rsim.get_field_params()
        self.max_pos = max(
            self.field.width / 2, (self.field.length / 2) + self.field.penalty_length
        )
        max_wheel_rad_s = (self.field.rbt_motor_max_rpm / 60) * 2 * np.pi
        self.max_v = max_wheel_rad_s * self.field.rbt_wheel_radius
        # 0.04 = robot radius (0.0375) + wheel thicknees (0.0025)
        self.max_w = np.rad2deg(self.max_v / 0.04)

        # Initiate
        self.frame: Frame = None
        self.last_frame: Frame = None
        self.view = None
        self.steps = 0
        self.sent_commands = None

        # Manage render modes
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

    def step(self, action):
        self.steps += 1
        # Join agent action with environment actions
        commands: List[Robot] = self._get_commands(action)
        # Send command to simulator
        self.rsim.send_commands(commands)
        self.sent_commands = commands

        # Get Frame from simulator
        self.last_frame = self.frame
        self.frame = self.rsim.get_frame()

        # Calculate environment observation, reward, terminated and truncated condition
        observation = self._frame_to_observations()
        reward, terminated = self._calculate_reward_and_done()
        truncated = False
        if self.steps >= self.MAX_EPISODE_STEPS: 
            truncated = True

        # Call render method
        if self.render_mode is not None:
            self.render()

        return observation, reward, terminated, truncated, {}

    def reset(self, seed=None, options=None):
        # Seed the random number generator
        super().reset(seed=seed)

        self.steps = 0
        self.last_frame = None
        self.sent_commands = None

        # Close render window
        del self.view
        self.view = None

        initial_pos_frame: Frame = self._get_initial_positions_frame()
        self.rsim.reset(initial_pos_frame)

        # Get frame from simulator
        self.frame = self.rsim.get_frame()

        # Call render method
        if self.render_mode is not None:
            self.render()

        return self._frame_to_observations(), {}

    def render(self) -> None:
        """
        Renders the game depending on
        ball's and players' positions.

        Parameters
        ----------
        None

        Returns
        -------
        None

        """
        if self.view == None:
            from rsoccer_gym.Render import RCGymRender

            self.view = RCGymRender(
                self.n_robots_blue, self.n_robots_yellow, self.field, render_mode=self.render_mode, simulator="vss"
            )

        return self.view.render_frame(self.frame)

    def close(self):
        self.rsim.stop()
        del self.view

    def _get_commands(self, action):
        """returns a list of commands of type List[Robot] from type action_space action"""
        raise NotImplementedError

    def _frame_to_observations(self):
        """returns a type observation_space observation from a type List[Robot] state"""
        raise NotImplementedError

    def _calculate_reward_and_done(self):
        """returns reward value and done flag from type List[Robot] state"""
        raise NotImplementedError

    def _get_initial_positions_frame(self) -> Frame:
        """returns frame with robots initial positions"""
        raise NotImplementedError

    def norm_pos(self, pos):
        return np.clip(pos / self.max_pos, -self.NORM_BOUNDS, self.NORM_BOUNDS)

    def norm_v(self, v):
        return np.clip(v / self.max_v, -self.NORM_BOUNDS, self.NORM_BOUNDS)

    def norm_w(self, w):
        return np.clip(w / self.max_w, -self.NORM_BOUNDS, self.NORM_BOUNDS)
