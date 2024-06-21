import math
from Code.utilities import rgba_to_glsl, percent_to_rgba, COLORS, get_text_height, get_text_width, point_is_in_ltwh, IMAGE_PATHS, loading_and_unloading_images_manager, LOADED_IN_EDITOR, OFF_SCREEN, move_number_to_desired_range
from Code.Editor.editor_update import update_header, update_footer, update_separate_palette_and_add_color, update_tools, update_palette
from Code.Editor.editor_utilities import DynamicInput


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
        self.palette_scroll_background_color = COLORS['BLACK']
        self.palette_colors = [COLORS['RED'], COLORS['GREEN'], COLORS['BLUE'], COLORS['YELLOW'], COLORS['RED'], COLORS['GREEN'], COLORS['BLUE'], COLORS['YELLOW'], COLORS['BLACK'], COLORS['WHITE'], COLORS['GREY'], rgba_to_glsl((0, 0, 0, 0)), rgba_to_glsl((64, 64, 64, 0)), rgba_to_glsl((128, 128, 128, 0)), rgba_to_glsl((192, 192, 192, 0)), rgba_to_glsl((0, 255, 255, 128))]
        self.palette_colors_per_row = 5
        self.palette_padding = 5
        self.palette_color_wh = [35, 35]
        self.palette_space_between_colors_and_scroll = 8
        self.palette_scroll_width = 22
        self.palette_color_border_thickness = 2
        self.palette_ltwh = [0, self.header_bottom, (2 * self.palette_padding) + (self.palette_colors_per_row * self.palette_color_wh[0]) + self.palette_space_between_colors_and_scroll + self.palette_scroll_width - (self.palette_color_border_thickness * (self.palette_colors_per_row) - 1), 0]
        self.currently_selected_color = CurrentlySelectedColor(self.palette_colors[0], 0, self.palette_color_wh[0])
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
        self.add_color_input_space_between_inputs = 12
        self.add_color_input_text_pixel_size = 3
        self.add_color_input_single_input_height = self.add_color_input_space_between_inputs + get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size)
        self.add_color_inputs = ['R', 'G', 'B', 'A']
        self.add_color_input_equals_symbol = '='
        self.add_color_input_max_length = 0
        self.add_color_input_max_length = max([get_text_width(Render, character, self.add_color_input_text_pixel_size) for character in self.add_color_inputs])
        self.add_color_input_top = self.add_color_spectrum_ltwh[1] + self.add_color_spectrum_ltwh[3]
        self.add_color_input_color_equals_input_left = [self.palette_padding, self.palette_padding + self.add_color_input_max_length + get_text_width(Render, ' ', self.add_color_input_text_pixel_size), self.palette_padding + self.add_color_input_max_length + get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) - self.add_color_input_text_pixel_size]
        self.add_color_input_height = (self.add_color_input_space_between_inputs * 5) + (4 * (get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size)))
        self.add_color_dynamic_inputs = [DynamicInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         DynamicInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         DynamicInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),
                                         DynamicInput([self.add_color_input_color_equals_input_left[2], 0, self.palette_ltwh[2] - (2 * self.palette_padding) - self.add_color_input_max_length - get_text_width(Render, ' = ', self.add_color_input_text_pixel_size) + self.add_color_input_text_pixel_size, get_text_height(self.add_color_input_text_pixel_size) - (2 * self.add_color_input_text_pixel_size) + (self.add_color_input_space_between_inputs / 2)], self.add_color_input_background_color, self.add_color_input_inputs_and_equals_color, self.add_color_input_text_pixel_size, (self.add_color_input_space_between_inputs / 4), allowable_range=[0, 255], is_an_int=True, must_fit=True, default_value='0'),]
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



class CurrentlySelectedColor():
    def __init__(self, color, palette_index, base_box_size):
        #
        # input parameters
        self.color = color
        self.color_max_saturation = color
        self.color_min_saturation = color
        self.color_max_alpha = color
        self.color_no_alpha = color
        self.palette_index = palette_index
        self.palette_ltwh = [0, 0, base_box_size, base_box_size]
        #
        # mode of selection; palette/spectrum
        self.selected_through_palette = True
        #
        # palette selection properties
        self.outline1_color = COLORS['YELLOW']
        self.outline1_thickness = 2
        self.outline1_ltwh = [0, 0, base_box_size + (2 * self.outline1_thickness), base_box_size + (2 * self.outline1_thickness)]
        self.outline2_color = COLORS['BLACK']
        self.outline2_thickness = 4
        self.outline2_ltwh = [0, 0, base_box_size + (2 * self.outline2_thickness), base_box_size + (2 * self.outline2_thickness)]
        self.checker_pattern_repeat = 5
        self.checker_color1 = COLORS['GREY']
        self.checker_color2 = COLORS['WHITE']
        #
        # spectrum selection properties
        self.red = 0.0
        self.green = 0.0
        self.blue = 0.0
        self.saturation = 1.0
        self.alpha = 1.0
        self.calculate_color(0.0, 0.0, self.alpha)

    def update_outline_ltwh(self):
        self.outline1_ltwh[0] = self.palette_ltwh[0] - self.outline1_thickness
        self.outline1_ltwh[1] = self.palette_ltwh[1] - self.outline1_thickness
        self.outline2_ltwh[0] = self.palette_ltwh[0] - self.outline2_thickness
        self.outline2_ltwh[1] = self.palette_ltwh[1] - self.outline2_thickness

    def update_colors_with_saturation(self):
        self.color_max_saturation = (self.red, self.green, self.blue, 1.0)
        max_color = max([self.red, self.green, self.blue])
        min_color = min([self.red, self.green, self.blue])
        middle_color = ((max_color - min_color) / 2) + min_color
        adjustment = (middle_color * (1 - self.saturation))
        self.red = (self.red * self.saturation) + adjustment
        self.green = (self.green * self.saturation) + adjustment
        self.blue = (self.blue * self.saturation) + adjustment
        self.color_min_saturation = (middle_color, middle_color, middle_color, 1.0)

    def update_color(self):
        self.color = (self.red, self.green, self.blue, self.alpha)
        self.color_max_alpha = (self.red, self.green, self.blue, 1.0)
        self.color_no_alpha = (self.red, self.green, self.blue, 0.0)

    def calculate_color(self, spectrum_x, spectrum_y, alpha):
        self.alpha = alpha
        # in top half of spectrum
        if 0 <= spectrum_y <= 0.5:
            spectrum_y *= 2
            # section 0 across
            if (0 / 6) <= spectrum_x < (1 / 6):
                spectrum_x = (spectrum_x - (0 / 6)) * 6
                self.red = 1.0
                self.green = 1 - ((1 - spectrum_x) * spectrum_y)
                self.blue = (1 - spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 1 across
            if (1 / 6) <= spectrum_x < (2 / 6):
                spectrum_x = (spectrum_x - (1 / 6)) * 6
                self.red = 1.0 - (spectrum_x * spectrum_y)
                self.green = 1.0
                self.blue = (1 - spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 2 across
            if (2 / 6) <= spectrum_x < (3 / 6):
                spectrum_x = (spectrum_x - (2 / 6)) * 6
                self.red = (1.0 - spectrum_y)
                self.green = 1.0
                self.blue = 1.0 - ((1.0 - spectrum_x) * spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 3 across
            if (3 / 6) <= spectrum_x < (4 / 6):
                spectrum_x = (spectrum_x - (3 / 6)) * 6
                self.red = (1.0 - spectrum_y)
                self.green = 1.0 - (spectrum_x * spectrum_y)
                self.blue = 1.0
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 4 across
            if (4 / 6) <= spectrum_x < (5 / 6):
                spectrum_x = (spectrum_x - (4 / 6)) * 6
                self.red = 1.0 - ((1.0 - spectrum_x) * spectrum_y)
                self.green = (1.0 - spectrum_y)
                self.blue = 1.0
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 5 across
            if (5 / 6) <= spectrum_x <= (6 / 6):
                spectrum_x = (spectrum_x - (5 / 6)) * 6
                self.red = 1.0
                self.green = (1.0 - spectrum_y)
                self.blue = 1.0 - (spectrum_x * spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
        # in bottom half of spectrum
        else:
            spectrum_y = (spectrum_y - 0.5) * 2
            # section 0 across
            if (0 / 6) <= spectrum_x < (1 / 6):
                spectrum_x = (spectrum_x - (0 / 6)) * 6
                self.red = (1.0 - spectrum_y)
                self.green = spectrum_x * (1.0 - spectrum_y)
                self.blue = 0.0
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 1 across
            if (1 / 6) <= spectrum_x < (2 / 6):
                spectrum_x = (spectrum_x - (1 / 6)) * 6
                self.red = (1.0-spectrum_x) * (1.0-spectrum_y)
                self.green = (1.0 - spectrum_y)
                self.blue = 0.0
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 2 across
            if (2 / 6) <= spectrum_x < (3 / 6):
                spectrum_x = (spectrum_x - (2 / 6)) * 6
                self.red = 0.0
                self.green = (1.0 - spectrum_y)
                self.blue = spectrum_x * (1.0 - spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 3 across
            if (3 / 6) <= spectrum_x < (4 / 6):
                spectrum_x = (spectrum_x - (3 / 6)) * 6
                self.red = 0.0
                self.green = (1.0-spectrum_x) * (1.0-spectrum_y)
                self.blue = (1.0 - spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 4 across
            if (4 / 6) <= spectrum_x < (5 / 6):
                spectrum_x = (spectrum_x - (4 / 6)) * 6
                self.red = spectrum_x * (1.0 - spectrum_y)
                self.green = 0.0
                self.blue = (1.0 - spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return
            # section 5 across
            if (5 / 6) <= spectrum_x <= (6 / 6):
                spectrum_x = (spectrum_x - (5 / 6)) * 6
                self.red = (1.0 - spectrum_y)
                self.green = 0.0
                self.blue = (1.0-spectrum_x) * (1.0-spectrum_y)
                self.update_colors_with_saturation()
                self.update_color()
                return

    def rgb_to_hsl(self, rgb: list[float]):
        max_color = max([rgb[0], rgb[1], rgb[2]])
        min_color = min([rgb[0], rgb[1], rgb[2]])
        luminance = (max_color + min_color) / 2
        chroma = max_color - min_color
        if chroma == 0:
            luminance = 1 - luminance
            hue = 0
            saturation = 0
        else:
            saturation = chroma / (1 - abs(2 * luminance - 1))
            # red is biggest
            if (rgb[0] >= rgb[1]) and (rgb[0] >= rgb[2]): # red is biggest
                hue = (((rgb[1] - rgb[2]) / chroma) % 6) / 6
            # green is biggest
            if (rgb[1] >= rgb[0]) and (rgb[1] >= rgb[2]):
                hue = ((rgb[2] - rgb[0]) / chroma + 2) / 6
            # blue is biggest
            if (rgb[2] >= rgb[0]) and (rgb[2] >= rgb[1]):
                hue = ((rgb[0] - rgb[1]) / chroma + 4) / 6
        hue = move_number_to_desired_range(0, hue, 1)
        saturation = move_number_to_desired_range(0, saturation, 1)
        luminance = move_number_to_desired_range(0, luminance, 1)
        return [hue, saturation, luminance]


def update_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
    #
    # draw add color background
    Singleton.add_color_ltwh[1] = Singleton.footer_ltwh[1] - Singleton.add_color_ltwh[3]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.add_color_ltwh, Singleton.add_color_background_color)
    #
    # add/remove color button
    Singleton.add_color_words_background_ltwh[1] = Singleton.separate_palette_and_add_color_ltwh[1] + Singleton.separate_palette_and_add_color_ltwh[3] + Singleton.palette_padding
    if Singleton.currently_selected_color.color[3] < 1:
        Singleton.add_or_remove_checkerboard_ltwh[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness
        Render.checkerboard(Screen, gl_context, 'black_pixel', Singleton.add_or_remove_checkerboard_ltwh, Singleton.currently_selected_color.checker_color1, Singleton.currently_selected_color.checker_color2, Singleton.add_or_remove_checkerboard_repeat, Singleton.add_or_remove_checkerboard_repeat)
    Render.draw_rectangle(Screen, gl_context, Singleton.add_color_words_background_ltwh, Singleton.add_color_words_border_thickness, Singleton.add_color_words_border_color, True, Singleton.currently_selected_color.color, True)
    if not Singleton.currently_selected_color.selected_through_palette:
        Singleton.add_color_words_lt[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness + Singleton.add_color_words_padding
        Render.draw_string_of_characters(Screen, gl_context, Singleton.add_color_words, Singleton.add_color_words_lt, Singleton.add_color_words_text_pixel_size, Singleton.add_color_current_circle_color if Singleton.currently_selected_color.color[3] > 0.5 else COLORS['BLACK'])
    if Singleton.currently_selected_color.selected_through_palette:
        Singleton.remove_color_words_lt[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness + Singleton.add_color_words_padding
        Render.draw_string_of_characters(Screen, gl_context, Singleton.remove_color_words, Singleton.remove_color_words_lt, Singleton.add_color_words_text_pixel_size, Singleton.add_color_current_circle_color if Singleton.currently_selected_color.color[3] > 0.5 else COLORS['BLACK'])
    #
    # RGBA spectrum
    color_spectrum_ltwh = Singleton.get_color_spectrum_ltwh()
    Render.rgba_picker(Screen, gl_context, 'black_pixel', color_spectrum_ltwh, Singleton.currently_selected_color.saturation)
    mouse_is_in_spectrum = point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, color_spectrum_ltwh)
    if mouse_is_in_spectrum and Keys.editor_primary.newly_pressed:
        Singleton.add_color_circle_is_held = True
        Singleton.currently_selected_color.selected_through_palette = False
    if Singleton.add_color_circle_is_held:
        spectrum_x_pos = move_number_to_desired_range(0, (Keys.cursor_x_pos.value - color_spectrum_ltwh[0]), color_spectrum_ltwh[2])
        spectrum_y_pos = move_number_to_desired_range(0, (Keys.cursor_y_pos.value - color_spectrum_ltwh[1]), color_spectrum_ltwh[3])
        mouse_in_top_half_of_spectrum = (spectrum_y_pos / color_spectrum_ltwh[3]) > 0.5
        Singleton.add_color_current_circle_color = COLORS['WHITE'] if mouse_in_top_half_of_spectrum else COLORS['BLACK']
        Singleton.add_color_circle_center_relative_xy = [spectrum_x_pos, spectrum_y_pos]
        Singleton.add_color_spectrum_x_percentage = (spectrum_x_pos / color_spectrum_ltwh[2])
        Singleton.add_color_spectrum_y_percentage = (spectrum_y_pos / color_spectrum_ltwh[3])
        Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
        if Keys.editor_primary.released:
            Singleton.add_color_circle_is_held = False
    Singleton.add_color_circle_ltwh[0] = color_spectrum_ltwh[0] + Singleton.add_color_circle_center_relative_xy[0] - (Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH // 2)
    Singleton.add_color_circle_ltwh[1] = color_spectrum_ltwh[1] + Singleton.add_color_circle_center_relative_xy[1] - (Render.renderable_objects['editor_circle'].ORIGINAL_HEIGHT // 2)
    Render.basic_rect_ltwh_image_with_color(Screen, gl_context, 'editor_circle', Singleton.add_color_circle_ltwh, Singleton.add_color_current_circle_color)
    #
    # RGBA saturation
    Singleton.add_color_saturation_ltwh[1] = color_spectrum_ltwh[1] + color_spectrum_ltwh[3]
    Render.spectrum_x(Screen, gl_context, 'black_pixel', Singleton.add_color_saturation_ltwh, Singleton.currently_selected_color.color_min_saturation, Singleton.currently_selected_color.color_max_saturation)
    mouse_is_in_saturation = point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, Singleton.add_color_saturation_ltwh)
    if mouse_is_in_saturation and Keys.editor_primary.newly_pressed and not Singleton.add_color_circle_is_held:
        Singleton.add_color_saturation_circle_is_held = True
        Singleton.currently_selected_color.selected_through_palette = False
    if Singleton.add_color_saturation_circle_is_held:
        saturation_x_pos = move_number_to_desired_range(0, (Keys.cursor_x_pos.value - Singleton.add_color_saturation_ltwh[0]), color_spectrum_ltwh[2])
        Singleton.add_color_saturation_circle_relative_x = saturation_x_pos
        Singleton.currently_selected_color.saturation = Singleton.add_color_saturation_circle_relative_x / color_spectrum_ltwh[2]
        Singleton.add_color_saturation_percentage = (saturation_x_pos / color_spectrum_ltwh[2])
        Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
        if Keys.editor_primary.released:
            Singleton.add_color_saturation_circle_is_held = False
    Singleton.add_color_saturation_circle_ltwh[0] = Singleton.add_color_saturation_ltwh[0] + Singleton.add_color_saturation_circle_relative_x - (Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH // 2)
    Singleton.add_color_saturation_circle_ltwh[1] = Singleton.add_color_saturation_ltwh[1] + (Singleton.add_color_saturation_ltwh[3] // 2) - (Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH // 2)
    Render.basic_rect_ltwh_image_with_color(Screen, gl_context, 'editor_circle', Singleton.add_color_saturation_circle_ltwh, Singleton.add_color_current_circle_color)
    #
    # RGBA alpha
    Singleton.add_color_alpha_ltwh[1] = color_spectrum_ltwh[1] + color_spectrum_ltwh[3] + Singleton.add_color_saturation_ltwh[3]
    Render.checkerboard(Screen, gl_context, 'black_pixel', Singleton.add_color_alpha_ltwh, Singleton.add_color_alpha_checker_color1, Singleton.add_color_alpha_checker_color2, Singleton.add_color_alpha_checker_x, Singleton.add_color_alpha_checker_y)
    Render.spectrum_x(Screen, gl_context, 'black_pixel', Singleton.add_color_alpha_ltwh, Singleton.currently_selected_color.color_no_alpha, Singleton.currently_selected_color.color_max_alpha)
    mouse_is_in_alpha = point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, Singleton.add_color_alpha_ltwh)
    if mouse_is_in_alpha and Keys.editor_primary.newly_pressed and not Singleton.add_color_saturation_circle_is_held:
        Singleton.add_color_alpha_circle_is_held = True
        Singleton.currently_selected_color.selected_through_palette = False
    if Singleton.add_color_alpha_circle_is_held:
        alpha_x_pos = move_number_to_desired_range(0, (Keys.cursor_x_pos.value - Singleton.add_color_alpha_ltwh[0]), color_spectrum_ltwh[2])
        Singleton.add_color_alpha_circle_relative_x = alpha_x_pos
        Singleton.currently_selected_color.alpha = Singleton.add_color_alpha_circle_relative_x / color_spectrum_ltwh[2]
        Singleton.add_color_alpha_percentage = (alpha_x_pos / color_spectrum_ltwh[2])
        Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
        if Keys.editor_primary.released:
            Singleton.add_color_alpha_circle_is_held = False
    Singleton.add_color_alpha_circle_ltwh[0] = Singleton.add_color_alpha_ltwh[0] + Singleton.add_color_alpha_circle_relative_x - (Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH // 2)
    Singleton.add_color_alpha_circle_ltwh[1] = Singleton.add_color_alpha_ltwh[1] + (Singleton.add_color_alpha_ltwh[3] // 2) - (Render.renderable_objects['editor_circle'].ORIGINAL_WIDTH // 2)
    Render.basic_rect_ltwh_image_with_color(Screen, gl_context, 'editor_circle', Singleton.add_color_alpha_circle_ltwh, Singleton.add_color_current_circle_color)
    #
    # RBGA spectrum border
    spectrum_border_ltwh = [color_spectrum_ltwh[0] - Singleton.add_color_spectrum_border_thickness, color_spectrum_ltwh[1] - Singleton.add_color_spectrum_border_thickness, color_spectrum_ltwh[2] + (2 * Singleton.add_color_spectrum_border_thickness), color_spectrum_ltwh[3] + (2 * Singleton.add_color_spectrum_border_thickness) + Singleton.add_color_saturation_ltwh[3] + Singleton.add_color_alpha_ltwh[3]]
    Render.draw_rectangle(Screen, gl_context, spectrum_border_ltwh, Singleton.add_color_spectrum_border_thickness, Singleton.add_color_spectrum_border_color, True, COLORS['DEFAULT'], False)
    #
    # RGBA inputs
    Singleton.add_color_input_top = spectrum_border_ltwh[1] + spectrum_border_ltwh[3]
    current_character_top = Singleton.add_color_input_top + Singleton.add_color_input_space_between_inputs
    for index, input_character in enumerate(Singleton.add_color_inputs):
        Render.draw_string_of_characters(Screen, gl_context, input_character, [Singleton.add_color_input_color_equals_input_left[0], current_character_top], Singleton.add_color_input_text_pixel_size, Singleton.add_color_input_inputs_and_equals_color)
        Render.draw_string_of_characters(Screen, gl_context, '=', [Singleton.add_color_input_color_equals_input_left[1], current_character_top], Singleton.add_color_input_text_pixel_size, Singleton.add_color_input_inputs_and_equals_color)
        Singleton.add_color_dynamic_inputs[index].background_ltwh[1] = current_character_top
        Singleton.add_color_dynamic_inputs[index].update(Screen, gl_context, Keys, Render, offset_y=-Singleton.add_color_dynamic_inputs[index].text_padding / 2)
        current_character_top += Singleton.add_color_input_single_input_height


def editor_loop(Api, PATH, Screen, gl_context, Render, Time, Keys):
    if Api.setup_required:
        loading_and_unloading_images_manager(Screen, Render, gl_context, IMAGE_PATHS, [LOADED_IN_EDITOR], [])
        Api.api_initiated_singletons['Editor'] = Api.api_singletons['Editor'](Render)
        Api.setup_required = False
    #
    else:
        Singleton = Api.api_initiated_singletons[Api.current_api]
        update_header(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)
        update_footer(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)
        update_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)
        update_separate_palette_and_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)
        update_palette(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)
        update_tools(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys)