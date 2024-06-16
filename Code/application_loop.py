import pygame
import sys


def update_events(Screen):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        #
        if event.type == pygame.VIDEORESIZE:
            Screen.width = event.w
            Screen.height = event.h
            Screen.update_aspect()
            Screen.screen = pygame.display.set_mode((Screen.width, Screen.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
            Screen.display = pygame.Surface((Screen.width, Screen.height))


def application_loop(Api, PATH, Screen, gl_context, Render, Time, Keys):
    while True:
        #
        # update events
        update_events(Screen)
        #
        # update keys
        Keys.update_controls()
        #
        # operate current API (e.g. Editor, Game, Menu)
        Api.api_options[Api.current_api](Api, PATH, Screen, gl_context, Render, Time, Keys)
        #
        # update screen
        Screen.update()
        Render.clear_buffer(gl_context)
        #
        # update timing
        Time.update()