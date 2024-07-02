import pygame
import sys
from Code.utilities import move_number_to_desired_range


def update_events(Screen):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        #
        if event.type == pygame.VIDEORESIZE:
            Screen.width = event.w
            Screen.height = event.h
            Screen.width = move_number_to_desired_range(Screen.ACCEPTABLE_WIDTH_RANGE[0], Screen.width, Screen.ACCEPTABLE_WIDTH_RANGE[1])
            Screen.height = move_number_to_desired_range(Screen.ACCEPTABLE_HEIGHT_RANGE[0], Screen.height, Screen.ACCEPTABLE_HEIGHT_RANGE[1])
            Screen.update_aspect()
            Screen.screen = pygame.display.set_mode((Screen.width, Screen.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            Screen.display = pygame.Surface((Screen.width, Screen.height))


def application_loop(Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    while True:
        #
        # update events
        update_events(Screen)
        #
        # update keys
        Keys.update_controls()
        #
        # operate current API (e.g. Editor, Game, Menu)
        Api.api_options[Api.current_api](Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        #
        # update screen
        Screen.update()
        Render.clear_buffer(gl_context)
        #
        # update timing
        Time.update()