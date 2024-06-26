import math
import random
from Code.utilities import rgba_to_glsl, percent_to_rgba, COLORS, get_text_height, get_text_width, point_is_in_ltwh, IMAGE_PATHS, loading_and_unloading_images_manager, LOADED_IN_EDITOR, OFF_SCREEN, move_number_to_desired_range, get_time, switch_to_base10, base10_to_hex, add_characters_to_front_of_string
from Code.Editor.editor_update import update_header, update_footer, update_separate_palette_and_add_color, update_tools, update_add_color
from Code.Editor.editor_utilities import TextInput, CurrentlySelectedColor


class EditorSingleton():
    def __init__(self, Render):
        self.border_color = COLORS['BLACK']
        #
        # header
        self.header_text_pixel_color = COLORS['BLACK']
        self.header_background_color = COLORS['PINK']
        self.header_highlight_color = (COLORS['YELLOW'][0], COLORS['YELLOW'][1], COLORS['YELLOW'][2], COLORS['YELLOW'][3] * 0.5)
        self.header_selected_color = COLORS['YELLOW']
        self.header_border_color = COLORS['WHITE']
        self.header_border_thickness = 2
        self.header_strings = ['File', 'Edit', 'Options', 'Objects', 'Blocks']
        self.header_string_selected = ''
        self.header_index_selected = -1
        self.header_indexes = [index for index in range(len(self.header_strings))]
        self.header_which_selected = [False for string in self.header_strings]
        self.header_selected = False
        self.header_padding = 10
        self.header_text_pixel_size = 3
        self.header_string_text_width = [get_text_width(Render, header_option, self.header_text_pixel_size) for header_option in self.header_strings]
        self.distance_between_header_options = 2 * self.header_padding
        current_left_position = self.distance_between_header_options
        self.header_strings_lefts = []
        self.header_strings_top = 0.5 * self.header_padding
        self.header_hover_ltwh = []
        self.header_height = self.header_padding + get_text_height(self.header_text_pixel_size) - (2 * self.header_text_pixel_size)
        for width in self.header_string_text_width:
            self.header_strings_lefts.append(current_left_position)
            hover_width = (self.distance_between_header_options * 2) + width
            self.header_hover_ltwh.append([current_left_position - self.distance_between_header_options, 0, hover_width, self.header_height])
            current_left_position += hover_width
        #
        self.header_strings_options = {'File': ['New', 'Open', 'Save' 'Main menu', 'Exit game'],
                                       'Edit': ['Undo', 'Paste', 'Rotate', 'Replace color', 'Flip'],
                                       'Options': ['Play level', 'Toggle map', 'Connect map', 'Grid'],
                                       'Objects': ['Object'],
                                       'Blocks': ['Block']}
        self.header_bottom = self.header_height + self.header_border_thickness
        #
        # palette
        self.palette_border_color = COLORS['PINK']
        self.palette_background_color = COLORS['GREY']
        self.palette_colors_border_color = COLORS['BLACK']
        self.palette_colors = [rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), 
                               rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), rgba_to_glsl((random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))), ]
        self.palette_colors_per_row = 5
        self.palette_padding = 5
        self.palette_color_wh = [35, 35]
        self.palette_space_between_colors_and_scroll = 8
        self.palette_scroll_width = 20
        self.palette_color_border_thickness = 2
        self.palette_ltwh = [0, self.header_bottom, (2 * self.palette_padding) + (self.palette_colors_per_row * self.palette_color_wh[0]) + self.palette_space_between_colors_and_scroll + self.palette_scroll_width - (self.palette_color_border_thickness * (self.palette_colors_per_row) - 1), 0]
        self.currently_selected_color = CurrentlySelectedColor(self.palette_colors[0], 0, self.palette_color_wh[0])
        self.palette_pressed_add_or_remove_button_this_frame = False
        # palette scroll bar
        self.palette_scroll_background_color = COLORS['WHITE']
        self.palette_scroll_outline_color = COLORS['BLUE']
        self.palette_scroll_inside_unhighlighted = rgba_to_glsl((255, 255, 255, 255))
        self.palette_scroll_inside_hightlighted = rgba_to_glsl((200, 200, 200, 255))
        self.palette_scroll_inside_grabbed = rgba_to_glsl((150, 150, 150, 255))
        self.palette_scroll_border_thickness = 4
        self.palette_scroll_colors_height = 0
        #
        # separate palette and add color
        self.separate_palette_and_add_color_color = COLORS['BLUE']
        self.separate_palette_and_add_color_ltwh = [0, 0, self.palette_ltwh[2], 2]
        #
        # footer
        self.footer_color = COLORS['BLUE']
        self.footer_ltwh = [0, 0, 0, self.header_height]
        #
        # add color
        # add/remove color
        self.add_color_words_border_color = COLORS['BLACK']
        self.add_color_words_text_pixel_size = 3
        self.add_color_words_border_thickness = 5
        self.add_color_words_padding = 4
        self.add_color_words = "ADD COLOR"
        self.remove_color_words = "REMOVE COLOR"
        self.add_color_words_length = get_text_width(Render, self.add_color_words, self.add_color_words_text_pixel_size)
        self.remove_color_words_length = get_text_width(Render, self.remove_color_words, self.add_color_words_text_pixel_size)
        self.add_color_words_background_ltwh = [self.palette_padding, self.separate_palette_and_add_color_ltwh[1] + self.separate_palette_and_add_color_ltwh[3] + self.palette_padding, self.palette_ltwh[2] - (2 * self.palette_padding), get_text_height(self.add_color_words_text_pixel_size) - (2 * self.add_color_words_text_pixel_size) + (2 * self.add_color_words_border_thickness) + (2 * self.add_color_words_padding)]
        self.add_color_words_lt = [math.floor(self.add_color_words_background_ltwh[0] + (self.add_color_words_background_ltwh[2] / 2) - (self.add_color_words_length / 2)), self.add_color_words_background_ltwh[1] + self.add_color_words_border_thickness + self.add_color_words_padding]
        self.remove_color_words_lt = [math.floor(self.add_color_words_background_ltwh[0] + (self.add_color_words_background_ltwh[2] / 2) - (self.remove_color_words_length / 2)), self.add_color_words_background_ltwh[1] + self.add_color_words_border_thickness + self.add_color_words_padding]
        self.gap_between_add_or_remove_color_and_spectrum = 4
        self.add_or_remove_checkerboard_ltwh = [self.add_color_words_background_ltwh[0] + self.add_color_words_border_thickness, self.add_color_words_background_ltwh[1] + self.add_color_words_border_thickness, self.add_color_words_background_ltwh[2] - (2 * self.add_color_words_border_thickness), self.add_color_words_background_ltwh[3] - (2 * self.add_color_words_border_thickness)]
        self.add_or_remove_checkerboard_repeat = 32
        # spectrum
        self.add_color_background_color = COLORS['PINK']
        self.add_color_spectrum_border_color = COLORS['BLACK']
        self.add_color_spectrum_height = 150
        self.add_color_spectrum_border_thickness = self.add_color_words_border_thickness
        self.add_color_spectrum_ltwh = [self.palette_padding + self.add_color_spectrum_border_thickness, self.separate_palette_and_add_color_ltwh[1] + self.separate_palette_and_add_color_ltwh[3] + self.palette_padding + self.add_color_spectrum_border_thickness, self.palette_ltwh[2] - (2 * self.palette_padding) - (2 * self.add_color_spectrum_border_thickness), self.add_color_spectrum_height - (2 * self.add_color_spectrum_border_thickness)]
        self.add_color_circle_center_relative_xy = [0, 0]
        self.add_color_spectrum_x_percentage = 0.0
        self.add_color_spectrum_y_percentage = 0.0
        self.add_color_circle_ltwh = [self.add_color_spectrum_ltwh[0], OFF_SCREEN, Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH, Render.renderable_objects['editor_circle'].ORIGINAL_HEIGHT]
        self.add_color_circle_is_held = False
        self.add_color_current_circle_color = COLORS['BLACK'] # changes with left-click on spectrum
        self.add_color_saturation_ltwh = [self.add_color_spectrum_ltwh[0], self.add_color_spectrum_ltwh[1] + self.add_color_spectrum_ltwh[3], self.add_color_spectrum_ltwh[2], 13]
        self.add_color_saturation_circle_ltwh = [self.add_color_spectrum_ltwh[0], OFF_SCREEN, Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH, Render.renderable_objects['editor_circle'].ORIGINAL_HEIGHT]
        self.add_color_saturation_circle_is_held = False
        self.add_color_saturation_circle_relative_x = self.add_color_spectrum_ltwh[2]
        self.add_color_saturation_percentage = 1.0
        self.add_color_alpha_ltwh = [self.add_color_spectrum_ltwh[0], self.add_color_spectrum_ltwh[1] + self.add_color_spectrum_ltwh[3], self.add_color_spectrum_ltwh[2], 13]
        self.add_color_alpha_circle_ltwh = [self.add_color_spectrum_ltwh[0], OFF_SCREEN, Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH, Render.renderable_objects['editor_circle'].ORIGINAL_HEIGHT]
        self.add_color_alpha_circle_is_held = False
        self.add_color_alpha_circle_relative_x = self.add_color_spectrum_ltwh[2]
        self.add_color_alpha_percentage = 1.0
        self.add_color_alpha_checker_x = 7
        self.add_color_alpha_checker_y = 7
        self.add_color_alpha_checker_color1 = COLORS['GREY']
        self.add_color_alpha_checker_color2 = COLORS['WHITE']
        # rgba input
        self.add_color_input_inputs_and_equals_color = COLORS['BLACK']
        self.add_color_input_background_color = COLORS['LIGHT_GREY']
        self.add_color_input_highlighted_text_color = COLORS['WHITE']
        self.add_color_input_highlighted_background_color = COLORS['RED']
        self.add_color_input_space_between_inputs = 12
        self.add_color_input_text_pixel_size = 3
        self.add_color_input_single_input_height = self.add_color_input_space_between_inputs + get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size)
        self.add_color_inputs = ['R', 'G', 'B', 'A', 'HEX #']
        self.add_color_input_equals_symbol = '='
        self.add_color_input_max_length = 0
        self.add_color_input_max_length = max([get_text_width(Render, character, self.add_color_input_text_pixel_size) for character in self.add_color_inputs if len(character) == 1])
        self.add_color_input_top = self.add_color_spectrum_ltwh[1] + self.add_color_spectrum_ltwh[3]
        self.add_color_input_color_equals_input_left = [self.palette_padding, self.palette_padding + self.add_color_input_max_length + get_text_width(Render, ' ', self.add_color_input_text_pixel_size), self.palette_padding + self.add_color_input_max_length + get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) - self.add_color_input_text_pixel_size]
        self.add_color_input_height = (self.add_color_input_space_between_inputs * 6) + (5 * (get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size)))
        self.add_color_dynamic_inputs = [TextInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_highlighted_text_color, self.add_color_input_highlighted_background_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         TextInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_highlighted_text_color, self.add_color_input_highlighted_background_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         TextInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_highlighted_text_color, self.add_color_input_highlighted_background_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         TextInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_highlighted_text_color, self.add_color_input_highlighted_background_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         TextInput([self.palette_padding + get_text_width(Render, self.add_color_inputs[4], self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, 0, self.palette_ltwh[2] - (2 * self.palette_padding) - get_text_width(Render, self.add_color_inputs[4], self.add_color_input_text_pixel_size) - self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_highlighted_text_color, self.add_color_input_highlighted_background_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[switch_to_base10('00000000', 16), switch_to_base10('ffffffff', 16)], is_a_hex=True, show_front_zeros=True, number_of_digits=8, must_fit=True, default_value='00000000'),]
        self.add_color_input_moving_down = False
        self.add_color_input_last_move_time = get_time()
        self.add_color_input_initial_fast_move = get_time()
        self.add_color_input_time_before_fast_move = 0.50
        self.add_color_input_time_between_moves = 0.05
        self.add_color_ltwh = [0, 0, self.palette_ltwh[2], (2 * self.palette_padding) + self.add_color_words_background_ltwh[3] + self.gap_between_add_or_remove_color_and_spectrum + self.add_color_spectrum_height + self.add_color_saturation_ltwh[3] + self.add_color_alpha_ltwh[3] + self.add_color_input_height - self.palette_padding]
        #
        # tool bar
        self.tool_bar_color = COLORS['RED']
        self.tool_bar_glow_color = COLORS['WHITE']
        self.tool_bar_padding = 5
        self.tool_bar_outline_pixels = 3
        self.tool_bar_tool_width = Render.renderable_objects['Marquee rectangle'].ORIGINAL_WIDTH
        self.tool_bar_ltwh = [0, self.header_bottom, Render.renderable_objects['Marquee rectangle'].ORIGINAL_WIDTH + (2 * self.tool_bar_padding), 0]
        tool_bar_tool_names = ['Marquee rectangle', 'Lasso', 'Pencil', 'Eraser', 'Spray', 'Hand', 'Bucket',
                               'Line', 'Curvy line', 'Empty rectangle', 'Filled rectangle', 'Empty ellipse',
                               'Filled ellipse', 'Blur', 'Jumble', 'Eyedropper']
        self.tool_bar_tools_dict = {}
        for tool_name_index, tool_name in enumerate(tool_bar_tool_names):
            self.tool_bar_tools_dict[tool_name] = [[0, self.header_bottom + (Render.renderable_objects[tool_name].ORIGINAL_HEIGHT * tool_name_index) + (self.tool_bar_padding * (tool_name_index + 1)), Render.renderable_objects[tool_name].ORIGINAL_WIDTH, Render.renderable_objects[tool_name].ORIGINAL_HEIGHT], # ltwh
                                                   True if tool_name == 'Hand' else False # selected
                                                   ]
    def get_color_spectrum_ltwh(self):
        return [self.palette_padding + self.add_color_spectrum_border_thickness, 
                self.separate_palette_and_add_color_ltwh[1] + self.add_color_words_background_ltwh[3] + self.gap_between_add_or_remove_color_and_spectrum + self.separate_palette_and_add_color_ltwh[3] + self.palette_padding + self.add_color_spectrum_border_thickness, 
                self.palette_ltwh[2] - (2 * self.palette_padding) - (2 * self.add_color_spectrum_border_thickness), 
                self.add_color_spectrum_height - (2 * self.add_color_spectrum_border_thickness)]


def update_palette(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # draw palette boundaries
    Singleton.palette_ltwh[3] = Screen.height - Singleton.header_bottom - Singleton.add_color_ltwh[3] - Singleton.footer_ltwh[3] - Singleton.separate_palette_and_add_color_ltwh[3]
    Render.draw_rectangle(Screen, gl_context, (0, Singleton.header_bottom, Singleton.palette_ltwh[2], Singleton.palette_ltwh[3]), Singleton.palette_padding, Singleton.palette_border_color, True, Singleton.palette_background_color, True)
    #
    # draw scroll
    palette_scroll_background_ltwh = (Singleton.palette_ltwh[2] - Singleton.palette_padding - Singleton.palette_scroll_width, Singleton.palette_ltwh[1] + Singleton.palette_padding, Singleton.palette_scroll_width, Singleton.palette_ltwh[3] - (2 * Singleton.palette_padding))
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', palette_scroll_background_ltwh, Singleton.palette_scroll_background_color)
    number_of_palette_color_rows = ((len(Singleton.palette_colors) - 1) // Singleton.palette_colors_per_row) + 1
    height_for_palette_colors = number_of_palette_color_rows * Singleton.palette_color_wh[1]
    print(height_for_palette_colors, Singleton.palette_ltwh[3])
    if height_for_palette_colors > Singleton.palette_ltwh[3] + (2 * Singleton.palette_padding):
        pass
    #
    # draw colors
    for palette_color_index, palette_color in enumerate(Singleton.palette_colors):
        column = palette_color_index % Singleton.palette_colors_per_row
        row = palette_color_index // Singleton.palette_colors_per_row
        color_left = Singleton.palette_ltwh[0] + Singleton.palette_padding + (column * Singleton.palette_color_wh[0]) - (column * Singleton.palette_color_border_thickness)
        color_top = Singleton.palette_ltwh[1] + Singleton.palette_padding + (row * Singleton.palette_color_wh[1]) - (row * Singleton.palette_color_border_thickness)
        color_ltwh = (color_left, color_top, Singleton.palette_color_wh[0], Singleton.palette_color_wh[1])
        if palette_color[3] < 1:
            Render.checkerboard(Screen, gl_context, 'black_pixel', color_ltwh, Singleton.currently_selected_color.checker_color1, Singleton.currently_selected_color.checker_color2, Singleton.currently_selected_color.checker_pattern_repeat, Singleton.currently_selected_color.checker_pattern_repeat)
        Render.draw_rectangle(Screen, gl_context, color_ltwh, Singleton.palette_color_border_thickness, Singleton.palette_colors_border_color, True, palette_color, True)
        if (Keys.editor_primary.newly_pressed and point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, color_ltwh)) or ((Singleton.currently_selected_color.palette_index == palette_color_index) and Singleton.palette_pressed_add_or_remove_button_this_frame):
            Singleton.currently_selected_color.selected_through_palette = True
            Singleton.currently_selected_color.color = palette_color
            Singleton.currently_selected_color.palette_index = palette_color_index
            # update spectrum based on palette selection
            Singleton.add_color_spectrum_x_percentage, Singleton.add_color_saturation_percentage, Singleton.add_color_spectrum_y_percentage = Singleton.currently_selected_color.rgb_to_hsl(Singleton.currently_selected_color.color)
            Singleton.add_color_alpha_percentage = Singleton.currently_selected_color.color[3]
            color_spectrum_ltwh = Singleton.get_color_spectrum_ltwh()
            # update spectrum
            spectrum_x_pos = move_number_to_desired_range(0, Singleton.add_color_spectrum_x_percentage * color_spectrum_ltwh[2], color_spectrum_ltwh[2])
            spectrum_y_pos = move_number_to_desired_range(0, Singleton.add_color_spectrum_y_percentage * color_spectrum_ltwh[3], color_spectrum_ltwh[3])
            mouse_in_bottom_half_of_spectrum = (spectrum_y_pos / color_spectrum_ltwh[3]) < 0.5
            Singleton.add_color_current_circle_color = COLORS['WHITE'] if mouse_in_bottom_half_of_spectrum else COLORS['BLACK']
            Singleton.add_color_circle_center_relative_xy = [spectrum_x_pos, abs(color_spectrum_ltwh[3] - spectrum_y_pos)]
            Singleton.add_color_spectrum_x_percentage = (spectrum_x_pos / color_spectrum_ltwh[2])
            Singleton.add_color_spectrum_y_percentage = abs(1 - (spectrum_y_pos / color_spectrum_ltwh[3]))
            # update saturation
            saturation_x_pos = move_number_to_desired_range(0, Singleton.add_color_saturation_percentage * color_spectrum_ltwh[2], color_spectrum_ltwh[2])
            Singleton.add_color_saturation_circle_relative_x = saturation_x_pos
            Singleton.currently_selected_color.saturation = Singleton.add_color_saturation_circle_relative_x / color_spectrum_ltwh[2]
            Singleton.add_color_saturation_percentage = (saturation_x_pos / color_spectrum_ltwh[2])
            # update alpha
            alpha_x_pos = move_number_to_desired_range(0, Singleton.add_color_alpha_percentage * color_spectrum_ltwh[2], color_spectrum_ltwh[2])
            Singleton.add_color_alpha_circle_relative_x = alpha_x_pos
            Singleton.currently_selected_color.alpha = Singleton.add_color_alpha_circle_relative_x / color_spectrum_ltwh[2]
            Singleton.add_color_alpha_percentage = (alpha_x_pos / color_spectrum_ltwh[2])
            # update the currently selected color
            Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
            # update text input displaying rgba and hex
            red, green, blue, alpha = [color_component for color_component in percent_to_rgba((Singleton.currently_selected_color.color))]
            Singleton.add_color_dynamic_inputs[0].current_string = str(red)
            Singleton.add_color_dynamic_inputs[1].current_string = str(green)
            Singleton.add_color_dynamic_inputs[2].current_string = str(blue)
            Singleton.add_color_dynamic_inputs[3].current_string = str(alpha)
            Singleton.add_color_dynamic_inputs[4].current_string = f'{add_characters_to_front_of_string(base10_to_hex(red), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(green), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(blue), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(alpha), 2, "0")}'
        if (Singleton.currently_selected_color.palette_index == palette_color_index):
            Singleton.currently_selected_color.palette_ltwh[0] = color_ltwh[0]
            Singleton.currently_selected_color.palette_ltwh[1] = color_ltwh[1]
            Singleton.currently_selected_color.update_outline_ltwh()
    #
    # draw selected palette color outline
    if Singleton.currently_selected_color.selected_through_palette and len(Singleton.palette_colors) > 0:
        Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.currently_selected_color.outline2_ltwh, Singleton.currently_selected_color.outline2_color)
        Render.checkerboard(Screen, gl_context, 'black_pixel', Singleton.currently_selected_color.outline1_ltwh, Singleton.currently_selected_color.checker_color1, Singleton.currently_selected_color.checker_color2, Singleton.currently_selected_color.checker_pattern_repeat, Singleton.currently_selected_color.checker_pattern_repeat)
        Render.draw_rectangle(Screen, gl_context, Singleton.currently_selected_color.outline1_ltwh, Singleton.currently_selected_color.outline1_thickness, Singleton.currently_selected_color.outline1_color, True, Singleton.currently_selected_color.color, True)


def editor_loop(Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    if Api.setup_required:
        loading_and_unloading_images_manager(Screen, Render, gl_context, IMAGE_PATHS, [LOADED_IN_EDITOR], [])
        Api.api_initiated_singletons['Editor'] = Api.api_singletons['Editor'](Render)
        Api.setup_required = False
    #
    else:
        Singleton = Api.api_initiated_singletons[Api.current_api]
        update_header(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        update_footer(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        update_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        update_separate_palette_and_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        update_palette(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)
        update_tools(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor)