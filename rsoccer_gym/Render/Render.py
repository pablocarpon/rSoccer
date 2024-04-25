import os

import numpy as np
from rsoccer_gym.Entities import Frame, Field
import pygame
from typing import Dict, List, Tuple

# COLORS RGB
BLACK =         (0   , 0   , 0   )
BG_GREEN =      (20  , 90  , 45  )
LINES_WHITE =   (220 , 220 , 220 )
ROBOT_BLACK =   (25  , 25  , 25  )
BALL_ORANGE =   (253 , 106 , 2   )
TAG_BLUE =      (0   , 64  , 255 )
TAG_YELLOW =    (250 , 218 , 94  )
TAG_GREEN =     (57  , 220 , 20  )
TAG_RED =       (151 , 21  , 0   )
TAG_PURPLE =    (102 , 51  , 153 )
TAG_PINK =      (220 , 0   , 220 )

class RCGymRender:
    '''
    Rendering Class to RoboSim Simulator, based on gym classic control rendering
    '''

    def __init__(self, n_robots_blue: int,
                 n_robots_yellow: int,
                 field_params: Field,
                 render_mode: str = None,
                 simulator: str = 'vss',
                 width: int = 750,
                 height: int = 650) -> None:
        '''
        Creates our View object.

        Parameters
        ----------
        n_robots_blue : int
            Number of blue robots

        n_robots_yellow : int
            Number of yellow robots

        field_params : Field
            field parameters

        simulator : str


        Returns
        -------
        None

        '''
        self.n_robots_blue = n_robots_blue
        self.n_robots_yellow = n_robots_yellow
        self.field = field_params
        self.screen = None
        self.clock = None
        self.canvas = None

        # Render mode
        self.render_mode = render_mode

        # Window dimensions in pixels
        screen_width = width
        screen_height = height

        # Field dimensions
        self.field_length = field_params.length
        self.field_width = field_params.width

        # Ratio between screen and field
        self.screen_field_ratio = screen_width / self.field_length

        # Init window if it isn't inicialiced
        if self.render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            self.clock = pygame.time.Clock()

        # Init canvas to draw the figures in it
        self.canvas = pygame.Surface((screen_width, screen_height))

        # Add background
        self._add_background()


    def __del__(self):
        if self.screen is not None:
            pygame.display.quit()
            pygame.quit()
        self.clock = None


    def render_frame(self, frame: Frame) -> None:
        '''
        Draws the field, ball and players.

        Parameters
        ----------
        Frame

        Returns
        -------
        None

        '''
        # Clear canvas surface
        self.canvas.fill(BLACK)

        # Add field lines
        self._add_field_lines_vss()

        # Add the ball to the field
        self._add_ball(frame)

        # Add all the robots to the field
        self._add_vss_robots(frame)

        if self.render_mode == "human":
            self.screen.blit(self.canvas, self.canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()
            self.clock.tick(75)
        elif self.render_mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.canvas), axes=(1,0,2))
            )


    def _add_background(self) -> None:
        self.canvas.fill(BLACK)


    def _add_ball(self, frame):
        ball_radius: float = self.field.ball_radius * self.screen_field_ratio
        x = (frame.ball.x + self.field_length/2) * self.screen_field_ratio
        y = (-frame.ball.y + self.field_width/2) * self.screen_field_ratio

        pygame.draw.circle(self.canvas, BALL_ORANGE, (x,y), ball_radius)
        pygame.draw.circle(self.canvas, BLACK, (x,y), ball_radius, 1)

    #----------VSS-----------#
    
    def _add_field_lines_vss(self) -> None:
        # Vertical Lines X
        x_border = self.field_length * self.screen_field_ratio
        x_penalty = [
            self.field.penalty_length*self.screen_field_ratio,
            x_border - self.field.penalty_length*self.screen_field_ratio
        ]
        x_center = x_border / 2

        # Horizontal Lines Y
        y_border = self.field_width * self.screen_field_ratio
        y_center = y_border / 2
        y_penalty = [
            y_center - self.field.penalty_width/2*self.screen_field_ratio,
            y_center + self.field.penalty_width/2*self.screen_field_ratio
        ]
        y_goal = [
            y_center - self.field.goal_width/2*self.screen_field_ratio, 
            y_center + self.field.goal_width/2*self.screen_field_ratio
        ]

        # Center line and circle
        pygame.draw.line(
            self.canvas, 
            LINES_WHITE, 
            (x_center, 0), 
            (x_center, y_border), 
            5
        )
        pygame.draw.circle(
            self.canvas,
            LINES_WHITE,
            (x_center, y_center),
            100,
            5
        )

        # Right side penalty box
        penalty_box_right_points = [
            (x_border, y_penalty[0]),
            (x_penalty[1], y_penalty[0]),
            (x_penalty[1], y_penalty[1]),
            (x_border, y_penalty[1])
        ]
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_right_points[0], penalty_box_right_points[1], 5)
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_right_points[1], penalty_box_right_points[2], 5)
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_right_points[2], penalty_box_right_points[3], 5)

        # Left side penalty box
        penalty_box_left_points = [
            (0, y_penalty[0]),
            (x_penalty[0], y_penalty[0]),
            (x_penalty[0], y_penalty[1]),
            (0, y_penalty[1])
        ]
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_left_points[0], penalty_box_left_points[1], 5)
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_left_points[1], penalty_box_left_points[2], 5)
        pygame.draw.line(self.canvas, LINES_WHITE, penalty_box_left_points[2], penalty_box_left_points[3], 5)

        # Right side goal
        pygame.draw.circle(self.canvas, LINES_WHITE, (x_border,y_goal[0]), 15)
        pygame.draw.circle(self.canvas, LINES_WHITE, (x_border,y_goal[1]), 15)

        # Left side goal 
        pygame.draw.circle(self.canvas, LINES_WHITE, (0,y_goal[0]), 15)
        pygame.draw.circle(self.canvas, LINES_WHITE, (0,y_goal[1]), 15)


    def _add_vss_robots(self, frame) -> None:
        tag_id_colors: Dict[int, Tuple[float, float, float]] = {
            0 : TAG_GREEN,
            1 : TAG_PURPLE,
            2 : TAG_RED
        }
        
        # Add blue robots
        for i, blue in enumerate(frame.robots_blue.values()):
            self._add_vss_robot(
                team_color=TAG_BLUE, id_color=tag_id_colors[i], x=blue.x, y=blue.y, theta=blue.theta
            )
            
        # Add yellow robots
        for i, yellow in enumerate(frame.robots_yellow.values()):
            self._add_vss_robot(
                team_color=TAG_YELLOW, id_color=tag_id_colors[i], x=yellow.x, y=yellow.y, theta=yellow.theta
            )


    def _add_vss_robot(self, team_color, id_color, x, y, theta):
        # Robot dimensions
        robot_x: float = (self.field.rbt_radius*2) * self.screen_field_ratio
        robot_y: float = (self.field.rbt_radius*2) * self.screen_field_ratio
        # Tag dimensions
        tag_x: float = robot_x // 2
        tag_y: float = robot_y 

        # Robot position
        x = (x + self.field_length/2) * self.screen_field_ratio
        y = (-y + self.field_width/2) * self.screen_field_ratio

        # Create a pygame surface to draw a robot
        robot_surf = pygame.Surface((robot_x,robot_y), pygame.SRCALPHA)

        # Draw robot team tag
        pygame.draw.rect(robot_surf, team_color, (tag_x,0,tag_x,tag_y))
        # Draw robot identifier
        pygame.draw.rect(robot_surf, id_color, (0,0,tag_x//2,tag_y))

        # Rotate robot surface
        rotated_robot_surf = pygame.transform.rotate(robot_surf, theta)

        # Obtein rect object that represents robot
        rotated_robot_rect = rotated_robot_surf.get_rect()

        # Place robot in its position
        rotated_robot_rect.center = (x, y)

        # Draw the robot in canvas
        self.canvas.blit(rotated_robot_surf, rotated_robot_rect)