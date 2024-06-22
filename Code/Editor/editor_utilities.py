from Code.utilities import point_is_in_ltwh, move_number_to_desired_range, get_text_width, get_time
import time
import math


class DynamicInput():
    def __init__(self, 
                 background_ltwh: list[int], 
                 background_color: list[float], 
                 text_color: list[float], 
                 text_pixel_size: int, 
                 text_padding: int, 
                 allowable_range: list[float | int, float | int] = [-math.inf, math.inf], 
                 is_an_int: bool = False, 
                 is_a_float: bool = False,
                 must_fit: bool = False,
                 default_value: str = '0'):

        self.background_ltwh = background_ltwh
        self.background_color = background_color
        self.text_color = text_color
        self.text_pixel_size = text_pixel_size
        self.text_padding = text_padding
        self.allowable_range = allowable_range
        self.is_a_float = is_a_float
        self.is_an_int = is_an_int
        self.must_fit = must_fit
        self.default_value = default_value
        if self.is_a_float:
            self.allowable_keys = ['RETURN', 'DELETE', 'BACKSPACE', 'UP', 'DOWN', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
        if self.is_an_int:
            self.allowable_keys = ['RETURN', 'DELETE', 'BACKSPACE', 'UP', 'DOWN', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        #
        self.blinking_cycle_duration = 1.15 # whole blinking cycle
        self.fast_time = 0.05 # time before moving left/right again when holding down an arrow key
        self.time_before_fast = 0.5
        self.last_move_time = get_time()
        self.last_edit_time = get_time()
        self.time_when_left_or_right_was_newly_pressed = get_time()
        self.time_when_edit_key_was_newly_pressed = get_time()
        self.blinking_line_time = get_time()
        self.blinking_line_wh = [self.text_pixel_size, background_ltwh[3] - 2]
        self.currently_selected = False
        self.last_key = ''
        self.selected_index = 0
        self.current_string = '0123456789'
    #
    def deselect_box(self):
        self.currently_selected = False
        self.validate_value()
    #
    def validate_value(self):
        if self.current_string == '':
            self.current_string = self.default_value
            return
        if self.is_a_float: 
            if self.current_value_is_float():
                self.current_string = str(float(move_number_to_desired_range(self.allowable_range[0], float(self.current_string), self.allowable_range[1])))
                return
            else:
                self.current_string = self.default_value
                return
        if self.is_an_int:
            if self.current_value_is_int():
                self.current_string = str(round(move_number_to_desired_range(self.allowable_range[0], float(self.current_string), self.allowable_range[1])))
                return
            else:
                self.current_string = self.default_value
                return
    #
    def current_value_is_float(self):
        try:
            float(self.current_string)
            return True
        except:
            return False
    #
    def current_value_is_int(self):
        try:
            int(self.current_string)
            return True
        except:
            return False
    #
    def update(self, screen_instance, gl_context, keys_class_instance, render_instance, offset_x: int = 0, offset_y: int = 0):
        background_ltwh = self._update(screen_instance, gl_context, keys_class_instance, render_instance, offset_x, offset_y)
        render_instance.draw_string_of_characters(screen_instance, gl_context, self.current_string, [math.floor(background_ltwh[0] + self.text_padding), math.floor(background_ltwh[1] + self.text_padding)], self.text_pixel_size, self.text_color)
    #
    def _update(self, screen_instance, gl_context, keys_class_instance, render_instance, offset_x: int = 0, offset_y: int = 0):
        background_ltwh = [self.background_ltwh[0] + offset_x, self.background_ltwh[1] + offset_y, self.background_ltwh[2], self.background_ltwh[3]]
        render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', background_ltwh, self.background_color)
        cursor_inside_box = point_is_in_ltwh(keys_class_instance.cursor_x_pos.value, keys_class_instance.cursor_y_pos.value, background_ltwh)
        # not currently selected
        if not self.currently_selected:
            if not keys_class_instance.editor_primary.pressed:
                return background_ltwh
            if not cursor_inside_box:
                return background_ltwh
            self.currently_selected = True
            self.update_clicked_index(render_instance, keys_class_instance, background_ltwh)
            return background_ltwh
        # currently selected
        else:
            self.draw_blinking_line(screen_instance, gl_context, render_instance, background_ltwh)
            if keys_class_instance.editor_primary.pressed and not cursor_inside_box:
                self.deselect_box()
                return background_ltwh
            if keys_class_instance.editor_primary.newly_pressed and cursor_inside_box:
                self.update_clicked_index(render_instance, keys_class_instance, background_ltwh)
                return background_ltwh
            if keys_class_instance.editor_left.pressed or keys_class_instance.editor_right.pressed:
                self.update_arrow_key_index(keys_class_instance)
                return background_ltwh

            string_before_edit = self.current_string
            index_before_edit = self.selected_index
            self.update_with_typed_key(keys_class_instance)
            if not self.fits(render_instance, background_ltwh, self.current_string):
                self.current_string = string_before_edit
                self.selected_index = index_before_edit
            return background_ltwh
    #
    def get_typed_key(self, keys_class_instance):
        return keys_class_instance.keyboard_key_to_character()
    #
    def update_clicked_index(self, render_instance, keys_class_instance, background_ltwh):
        self.blinking_line_time = get_time()
        current_left = math.floor(background_ltwh[0] + self.text_padding)
        if keys_class_instance.cursor_x_pos.value < current_left:
            self.new_selected_index(0)
            return
        for index, character in enumerate(self.current_string):
            character_width = get_text_width(render_instance, character, self.text_pixel_size)
            if keys_class_instance.cursor_x_pos.value <= current_left + (character_width / 2):
                self.new_selected_index(index)
                return
            if current_left + (character_width / 2) < keys_class_instance.cursor_x_pos.value <= current_left + character_width:
                self.new_selected_index(index + 1)
                return
            current_left += character_width + self.text_pixel_size
        self.new_selected_index(len(self.current_string))
    #
    def update_arrow_key_index(self, keys_class_instance):
        if keys_class_instance.editor_left.newly_pressed:
            self.new_selected_index(self.selected_index - 1)
            self.time_when_left_or_right_was_newly_pressed = get_time()
            return
        if keys_class_instance.editor_right.newly_pressed:
            self.new_selected_index(self.selected_index + 1)
            self.time_when_left_or_right_was_newly_pressed = get_time()
            return
        current_time = get_time()
        if (current_time - self.time_when_left_or_right_was_newly_pressed > self.time_before_fast) and (current_time - self.last_move_time > self.fast_time):
            if keys_class_instance.editor_left.pressed:
                self.new_selected_index(self.selected_index - 1)
                return
            if keys_class_instance.editor_right.pressed:
                self.new_selected_index(self.selected_index + 1)
                return
    #
    def draw_blinking_line(self, screen_instance, gl_context, render_instance, background_ltwh):
        currently_blinking = ((get_time() - self.blinking_line_time) % self.blinking_cycle_duration) <= (self.blinking_cycle_duration / 2)
        if not currently_blinking:
            return
        current_left = math.floor(background_ltwh[0] + 1)
        for index, character in enumerate(self.current_string):
            character_width = get_text_width(render_instance, character, self.text_pixel_size)
            if self.selected_index == index:
                render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', [current_left, background_ltwh[1] + 1, self.blinking_line_wh[0], self.blinking_line_wh[1]], self.text_color)
                return
            current_left += character_width + self.text_pixel_size
        render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', [current_left, background_ltwh[1] + 1, self.blinking_line_wh[0], self.blinking_line_wh[1]], self.text_color)
    #
    def new_selected_index(self, new_value):
        self.last_move_time = get_time()
        self.blinking_line_time = get_time()
        self.selected_index = new_value
        self.selected_index = move_number_to_desired_range(0, self.selected_index, len(self.current_string))
    #
    def update_with_typed_key(self, keys_class_instance):
        current_key = self.get_typed_key(keys_class_instance)
        if current_key is None:
            self.last_key = ''
            return
        if not (current_key in self.allowable_keys):
            return
        new_press = False
        if current_key != self.last_key:
            new_press = True
            self.time_when_edit_key_was_newly_pressed = get_time()
        self.last_key = current_key
        current_time = get_time()
        editing_this_frame = new_press or ((current_time - self.time_when_edit_key_was_newly_pressed > self.time_before_fast) and (current_time - self.last_edit_time > self.fast_time))
        if not editing_this_frame:
            return

        match current_key:
            case 'RETURN':
                self.deselect_box()
                return
            
            case 'DELETE':
                if self.selected_index == len(self.current_string):
                    self.last_edit_time = get_time()
                    self.new_selected_index(len(self.current_string))
                else:
                    self.last_edit_time = get_time()
                    self.new_selected_index(self.selected_index)
                    self.current_string = self.current_string[:self.selected_index] + self.current_string[self.selected_index + 1:]

            case 'BACKSPACE':
                if self.selected_index == 0:
                    self.last_edit_time = get_time()
                    self.new_selected_index(0)
                    return
                else:
                    self.last_edit_time = get_time()
                    self.new_selected_index(self.selected_index - 1)
                    self.current_string = self.current_string[:self.selected_index] + self.current_string[self.selected_index + 1:]
                    return

            case 'UP':
                if self.is_an_int:
                    if not self.current_value_is_int():
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], int(self.current_string) + 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                    return
                if self.is_a_float:
                    if not self.current_value_is_float():
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], float(self.current_string) + 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                    return
                return

            case 'DOWN':
                if self.is_an_int:
                    if not self.current_value_is_int():
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], int(self.current_string) - 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                if self.is_a_float:
                    if not self.current_value_is_float():
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], float(self.current_string) - 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                    return
                return
            
            case _:
                self.last_edit_time = get_time()
                self.current_string = self.current_string[:self.selected_index] + current_key + self.current_string[self.selected_index:]
                self.new_selected_index(self.selected_index + 1)
                return
    #
    def fits(self, render_instance, background_ltwh, string):
        if not self.must_fit:
            return True
        text_width = get_text_width(render_instance, string, self.text_pixel_size)
        return text_width <= background_ltwh[2] - (2 * self.text_padding)

# tab, shift tab
# control a, c, v, z
# highlighting