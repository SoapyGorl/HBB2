from Code.utilities import point_is_in_ltwh, move_number_to_desired_range, get_text_width, get_text_height, get_time, str_can_be_int, str_can_be_float
import math


class TextInput():
    _STOPPING_CHARACTERS = ' ,.?!:;/\\[](){}'
    def __init__(self, 
                 background_ltwh: list[int], 
                 background_color: list[float], 
                 text_color: list[float], 
                 highlighted_text_color: list[float],
                 highlight_color: list[float],
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
        self.highlighted_text_color = highlighted_text_color
        self.highlight_color = highlight_color
        self.text_pixel_size = text_pixel_size
        self.text_padding = text_padding
        self.allowable_range = allowable_range
        self.is_a_float = is_a_float
        self.is_an_int = is_an_int
        self.must_fit = must_fit
        self.default_value = default_value
        if self.is_a_float:
            self.allowable_keys = ['RETURN', 'DELETE', 'BACKSPACE', 'UP', 'DOWN', 'CTRL_A', 'CTRL_C', 'CTRL_V', 'CTRL_X', 'CTRL_BACKSPACE', 'CTRL_DELETE', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
        if self.is_an_int:
            self.allowable_keys = ['RETURN', 'DELETE', 'BACKSPACE', 'UP', 'DOWN', 'CTRL_A', 'CTRL_C', 'CTRL_V', 'CTRL_X', 'CTRL_BACKSPACE', 'CTRL_DELETE', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        #
        self.text_height = get_text_height(self.text_pixel_size) - (2 * self.text_pixel_size)
        self.highlighted_index_range = [2, 5]
        self.blinking_cycle_duration = 1.15 # whole blinking cycle
        self.fast_time = 0.05 # time before moving left/right again when holding down an arrow key
        self.time_before_fast = 0.5
        self.last_move_time = get_time()
        self.last_edit_time = get_time()
        self.time_when_left_or_right_was_newly_pressed = get_time()
        self.time_when_edit_key_was_newly_pressed = get_time()
        self.blinking_line_time = get_time()
        self.last_new_primary_click_time = get_time()
        self.double_click_time = 0.3
        self.double_clicked = False
        self.double_clicked_last_frame = False
        self.blinking_line_wh = [self.text_pixel_size, background_ltwh[3] - 2]
        self.currently_selected = False
        self.currently_highlighting = False
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
            if str_can_be_float(self.current_string):
                self.current_string = str(float(move_number_to_desired_range(self.allowable_range[0], float(self.current_string), self.allowable_range[1])))
                return
            else:
                self.current_string = self.default_value
                return
        if self.is_an_int:
            if str_can_be_int(self.current_string):
                self.current_string = str(round(move_number_to_desired_range(self.allowable_range[0], float(self.current_string), self.allowable_range[1])))
                return
            else:
                self.current_string = self.default_value
                return
    #
    def update(self, screen_instance, gl_context, keys_class_instance, render_instance, offset_x: int = 0, offset_y: int = 0):
        self.double_clicked_last_frame = self.double_clicked
        background_ltwh = self._update(screen_instance, gl_context, keys_class_instance, render_instance, offset_x, offset_y)
        if not self.currently_selected:
            render_instance.draw_string_of_characters(screen_instance, gl_context, self.current_string, [math.floor(background_ltwh[0] + self.text_padding), math.floor(background_ltwh[1] + self.text_padding)], self.text_pixel_size, self.text_color)
        else:
            start_left, top = [math.floor(background_ltwh[0] + self.text_padding), math.floor(background_ltwh[1] + self.text_padding)]
            small_highlight_index = min(self.highlighted_index_range)
            big_highlight_index  = max(self.highlighted_index_range)
            if small_highlight_index != big_highlight_index:
                string1 = self.current_string[:small_highlight_index] # not highlighted
                string2 = self.current_string[small_highlight_index:big_highlight_index] # highlighted
                string3 = self.current_string[big_highlight_index:] # not highlighted
                string1_width = get_text_width(render_instance, string1, self.text_pixel_size) + self.text_pixel_size
                string2_width = get_text_width(render_instance, string2, self.text_pixel_size) + self.text_pixel_size
                render_instance.draw_string_of_characters(screen_instance, gl_context, string1, [start_left, top], self.text_pixel_size, self.text_color)
                render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', [start_left+string1_width-1, background_ltwh[1] + self.text_padding - 1, string2_width-self.text_pixel_size+2, self.text_height + 2], self.highlight_color)
                render_instance.draw_string_of_characters(screen_instance, gl_context, string2, [start_left+string1_width, top], self.text_pixel_size, self.highlighted_text_color)
                render_instance.draw_string_of_characters(screen_instance, gl_context, string3, [start_left+string1_width+string2_width, top], self.text_pixel_size, self.text_color)
            if small_highlight_index == big_highlight_index:
                render_instance.draw_string_of_characters(screen_instance, gl_context, self.current_string, [math.floor(background_ltwh[0] + self.text_padding), math.floor(background_ltwh[1] + self.text_padding)], self.text_pixel_size, self.text_color)
            self.draw_blinking_line(screen_instance, gl_context, render_instance, background_ltwh)
    #
    def _update(self, screen_instance, gl_context, keys_class_instance, render_instance, offset_x: int = 0, offset_y: int = 0):
        background_ltwh = [self.background_ltwh[0] + offset_x, self.background_ltwh[1] + offset_y, self.background_ltwh[2], self.background_ltwh[3]]
        render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', background_ltwh, self.background_color)
        cursor_inside_box = point_is_in_ltwh(keys_class_instance.cursor_x_pos.value, keys_class_instance.cursor_y_pos.value, background_ltwh)
        double_clicked = self.update_double_click(keys_class_instance)
        if double_clicked:
            return background_ltwh
        # not currently selected
        if not self.currently_selected:
            if not keys_class_instance.editor_primary.pressed:
                return background_ltwh
            if not cursor_inside_box:
                return background_ltwh
            if keys_class_instance.editor_primary.newly_pressed:
                self.currently_selected = True
                self.initial_click(render_instance, keys_class_instance, background_ltwh)
            return background_ltwh
        # currently selected
        if self.currently_selected:
            if keys_class_instance.editor_primary.newly_pressed and not cursor_inside_box:
                self.deselect_box()
                return background_ltwh
            if keys_class_instance.editor_left.pressed or keys_class_instance.editor_right.pressed:
                self.update_arrow_key_index(keys_class_instance)
                return background_ltwh
            if keys_class_instance.editor_primary.newly_pressed and cursor_inside_box:
                self.initial_click(render_instance, keys_class_instance, background_ltwh)
                return background_ltwh
            if keys_class_instance.editor_primary.pressed and (self.highlighted_index_range[0] != -1) and not self.double_clicked_last_frame:
                self.released_click(render_instance, keys_class_instance, background_ltwh)
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
    def update_arrow_key_index(self, keys_class_instance):
        # just arrow key
        if not keys_class_instance.editor_shift.pressed and not keys_class_instance.editor_control.pressed:
            self.stop_highlighting()
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
        # shift and arrow key
        if keys_class_instance.editor_shift.pressed and not keys_class_instance.editor_control.pressed:
            if keys_class_instance.editor_left.newly_pressed:
                if (self.highlighted_index_range[0] == -1):
                    self.highlighted_index_range[0] = self.selected_index
                self.new_selected_index(self.selected_index - 1)
                self.highlighted_index_range[1] = self.selected_index
                self.update_currently_highlighting()
                self.time_when_left_or_right_was_newly_pressed = get_time()
                return
            if keys_class_instance.editor_right.newly_pressed:
                if (self.highlighted_index_range[0] == -1):
                    self.highlighted_index_range[0] = self.selected_index
                self.new_selected_index(self.selected_index + 1)
                self.highlighted_index_range[1] = self.selected_index
                self.update_currently_highlighting()
                self.time_when_left_or_right_was_newly_pressed = get_time()
                return
            current_time = get_time()
            if (current_time - self.time_when_left_or_right_was_newly_pressed > self.time_before_fast) and (current_time - self.last_move_time > self.fast_time):
                if keys_class_instance.editor_left.pressed:
                    self.new_selected_index(self.selected_index - 1)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                if keys_class_instance.editor_right.pressed:
                    self.new_selected_index(self.selected_index + 1)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
        # control and arrow key
        if not keys_class_instance.editor_shift.pressed and keys_class_instance.editor_control.pressed:
            self.stop_highlighting()
            if keys_class_instance.editor_left.newly_pressed:
                self.time_when_left_or_right_was_newly_pressed = get_time()
                found_desired_character, space_index = self.reverse_iterate_through_string_for_characters()
                if not found_desired_character:
                    self.new_selected_index(0)
                    return
                if space_index == 0:
                    self.new_selected_index(1)
                    return
                self.new_selected_index(space_index+1)
                return
            if keys_class_instance.editor_right.newly_pressed:
                self.time_when_left_or_right_was_newly_pressed = get_time()
                found_desired_character, space_index = self.iterate_through_string_for_character()
                if not found_desired_character:
                    self.new_selected_index(len(self.current_string))
                    return
                if self.selected_index + 1 + space_index == len(self.current_string):
                    self.new_selected_index(len(self.current_string) - 1)
                    return
                self.new_selected_index(self.selected_index+space_index)
                return
            current_time = get_time()
            if (current_time - self.time_when_left_or_right_was_newly_pressed > self.time_before_fast) and (current_time - self.last_move_time > self.fast_time):
                if keys_class_instance.editor_left.pressed:
                    found_desired_character, space_index = self.reverse_iterate_through_string_for_characters()
                    if not found_desired_character:
                        self.new_selected_index(0)
                        return
                    if space_index == 0:
                        self.new_selected_index(1)
                        return
                    self.new_selected_index(space_index+1)
                    return
                if keys_class_instance.editor_right.pressed:
                    found_desired_character, space_index = self.iterate_through_string_for_character()
                    if not found_desired_character:
                        self.new_selected_index(len(self.current_string))
                        return
                    if self.selected_index + 1 + space_index == len(self.current_string):
                        self.new_selected_index(len(self.current_string) - 1)
                        return
                    self.new_selected_index(self.selected_index+space_index)
                    return
        # control and shift and arrow key
        if keys_class_instance.editor_shift.pressed and keys_class_instance.editor_control.pressed:
            if keys_class_instance.editor_left.newly_pressed:
                self.time_when_left_or_right_was_newly_pressed = get_time()
                if (self.highlighted_index_range[0] == -1):
                    self.highlighted_index_range[0] = self.selected_index
                found_desired_character, space_index = self.reverse_iterate_through_string_for_characters()
                if not found_desired_character:
                    self.new_selected_index(0)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                if space_index == 0:
                    self.new_selected_index(1)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                self.new_selected_index(space_index+1)
                self.highlighted_index_range[1] = self.selected_index
                self.update_currently_highlighting()
                return
            if keys_class_instance.editor_right.newly_pressed:
                self.time_when_left_or_right_was_newly_pressed = get_time()
                if (self.highlighted_index_range[0] == -1):
                    self.highlighted_index_range[0] = self.selected_index
                found_desired_character, space_index = self.iterate_through_string_for_character()
                if not found_desired_character:
                    self.new_selected_index(len(self.current_string))
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                if self.selected_index + 1 + space_index == len(self.current_string):
                    self.new_selected_index(len(self.current_string) - 1)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                self.new_selected_index(self.selected_index+space_index)
                self.highlighted_index_range[1] = self.selected_index
                self.update_currently_highlighting()
                return
            current_time = get_time()
            if (current_time - self.time_when_left_or_right_was_newly_pressed > self.time_before_fast) and (current_time - self.last_move_time > self.fast_time):
                if keys_class_instance.editor_left.pressed:
                    if (self.highlighted_index_range[0] == -1):
                        self.highlighted_index_range[0] = self.selected_index
                    found_desired_character, space_index = self.reverse_iterate_through_string_for_characters()
                    if not found_desired_character:
                        self.new_selected_index(0)
                        self.highlighted_index_range[1] = self.selected_index
                        self.update_currently_highlighting()
                        return
                    if space_index == 0:
                        self.new_selected_index(1)
                        self.highlighted_index_range[1] = self.selected_index
                        self.update_currently_highlighting()
                        return
                    self.new_selected_index(space_index+1)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return
                if keys_class_instance.editor_right.pressed:
                    found_desired_character, space_index = self.iterate_through_string_for_character()
                    if (self.highlighted_index_range[0] == -1):
                        self.highlighted_index_range[0] = self.selected_index
                    found_desired_character, space_index = self.iterate_through_string_for_character()
                    if not found_desired_character:
                        self.new_selected_index(len(self.current_string))
                        self.highlighted_index_range[1] = self.selected_index
                        self.update_currently_highlighting()
                        return
                    if self.selected_index + 1 + space_index == len(self.current_string):
                        self.new_selected_index(len(self.current_string) - 1)
                        self.highlighted_index_range[1] = self.selected_index
                        self.update_currently_highlighting()
                        return
                    self.new_selected_index(self.selected_index+space_index)
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
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
    def fits(self, render_instance, background_ltwh, string):
        if not self.must_fit:
            return True
        text_width = get_text_width(render_instance, string, self.text_pixel_size)
        return text_width <= background_ltwh[2] - (2 * self.text_padding)
    #
    def initial_click(self, render_instance, keys_class_instance, background_ltwh):
        self.blinking_line_time = get_time()
        self.highlighted_index_range[0] = self.highlighted_index_range[1] = self.get_cursor_index(render_instance, keys_class_instance, background_ltwh)
        self.new_selected_index(self.highlighted_index_range[1])
        self.update_currently_highlighting()
    #
    def released_click(self, render_instance, keys_class_instance, background_ltwh):
        self.blinking_line_time = get_time()
        self.highlighted_index_range[1] = self.get_cursor_index(render_instance, keys_class_instance, background_ltwh)
        self.new_selected_index(self.highlighted_index_range[1])
        self.update_currently_highlighting()
    #
    def get_cursor_index(self, render_instance, keys_class_instance, background_ltwh):
        current_left = math.floor(background_ltwh[0] + self.text_padding)
        if keys_class_instance.cursor_x_pos.value < current_left:
            return 0
        for index, character in enumerate(self.current_string):
            character_width = get_text_width(render_instance, character, self.text_pixel_size)
            if keys_class_instance.cursor_x_pos.value <= current_left + (character_width / 2):
                return index
            if current_left + (character_width / 2) < keys_class_instance.cursor_x_pos.value <= current_left + character_width:
                return index + 1
            current_left += character_width + self.text_pixel_size
        return len(self.current_string)
    #
    def update_currently_highlighting(self):
        self.currently_highlighting = (self.highlighted_index_range[0] != self.highlighted_index_range[1]) and (self.highlighted_index_range[0] != -1) and (self.highlighted_index_range[1] != -1)
    #
    def stop_highlighting(self):
        self.highlighted_index_range[0] = self.highlighted_index_range[1] = -1
        self.currently_highlighting = False
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
                if self.currently_highlighting:
                    self.last_edit_time = get_time()
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    self.current_string = self.current_string[:lower_index] + self.current_string[higher_index:]
                    self.new_selected_index(lower_index)
                    self.stop_highlighting()
                    return
                if self.selected_index == len(self.current_string):
                    self.last_edit_time = get_time()
                    self.new_selected_index(len(self.current_string))
                    return
                if self.selected_index != len(self.current_string):
                    self.last_edit_time = get_time()
                    self.new_selected_index(self.selected_index)
                    self.current_string = self.current_string[:self.selected_index] + self.current_string[self.selected_index + 1:]
                    return

            case 'BACKSPACE':
                if self.currently_highlighting:
                    self.last_edit_time = get_time()
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    self.current_string = self.current_string[:lower_index] + self.current_string[higher_index:]
                    self.new_selected_index(lower_index)
                    self.stop_highlighting()
                    return
                if self.selected_index == 0:
                    self.last_edit_time = get_time()
                    self.new_selected_index(0)
                    return
                if self.selected_index != 0:
                    self.last_edit_time = get_time()
                    self.new_selected_index(self.selected_index - 1)
                    self.current_string = self.current_string[:self.selected_index] + self.current_string[self.selected_index + 1:]
                    return

            case 'UP':
                self.highlighted_index_range[0] = 0
                self.highlighted_index_range[1] = len(self.current_string)
                self.update_currently_highlighting()
                self.new_selected_index(len(self.current_string))
                if self.is_an_int:
                    if not str_can_be_int(self.current_string):
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], int(self.current_string) + 1, self.allowable_range[1]))
                    return
                if self.is_a_float:
                    if not str_can_be_float(self.current_string):
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], float(self.current_string) + 1, self.allowable_range[1]))
                    return
                return

            case 'DOWN':
                self.highlighted_index_range[0] = 0
                self.highlighted_index_range[1] = len(self.current_string)
                self.update_currently_highlighting()
                self.new_selected_index(len(self.current_string))
                if self.is_an_int:
                    if not str_can_be_int(self.current_string):
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], int(self.current_string) - 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                if self.is_a_float:
                    if not str_can_be_float(self.current_string):
                        return
                    self.last_edit_time = get_time()
                    self.current_string = str(move_number_to_desired_range(self.allowable_range[0], float(self.current_string) - 1, self.allowable_range[1]))
                    self.new_selected_index(len(self.current_string))
                    return
                return

            case 'CTRL_A':
                self.highlighted_index_range[0] = 0
                self.highlighted_index_range[1] = len(self.current_string)
                self.update_currently_highlighting()
                self.new_selected_index(len(self.current_string))
                return

            case 'CTRL_C':
                if not self.currently_highlighting:
                    return
                lower_index = min(self.highlighted_index_range)
                higher_index = max(self.highlighted_index_range)
                keys_class_instance.copy_text(self.current_string[lower_index:higher_index])
                return

            case 'CTRL_V':
                pasted_text = keys_class_instance.paste_text()
                for character in pasted_text:
                    if character not in self.allowable_keys:
                        return
                if not self.currently_highlighting:
                    potential_new_text = self.current_string[:self.selected_index] + pasted_text + self.current_string[self.selected_index:]
                if self.currently_highlighting:
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    potential_new_text = self.current_string[:lower_index] + pasted_text + self.current_string[higher_index:]
                if self.is_a_float:
                    if not str_can_be_float(potential_new_text):
                        return
                    self.current_string = potential_new_text
                    if not self.currently_highlighting:
                        self.new_selected_index(self.selected_index + len(pasted_text))
                    if self.currently_highlighting:
                        self.new_selected_index(lower_index + len(pasted_text))
                        self.stop_highlighting()
                        return
                if self.is_an_int:
                    if not str_can_be_int(potential_new_text):
                        return
                    self.current_string = potential_new_text
                    if not self.currently_highlighting:
                        self.new_selected_index(self.selected_index + len(pasted_text))
                    if self.currently_highlighting:
                        self.new_selected_index(lower_index + len(pasted_text))
                        self.stop_highlighting()
                        return
                return

            case 'CTRL_X':
                if not self.currently_highlighting:
                    return
                lower_index = min(self.highlighted_index_range)
                higher_index = max(self.highlighted_index_range)
                keys_class_instance.copy_text(self.current_string[lower_index:higher_index])
                self.current_string = self.current_string[:lower_index] + self.current_string[higher_index:]
                self.selected_index = lower_index
                self.stop_highlighting()
                return

            case 'CTRL_BACKSPACE':
                if self.currently_highlighting:
                    self.last_edit_time = get_time()
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    self.current_string = self.current_string[:lower_index] + self.current_string[higher_index:]
                    self.new_selected_index(lower_index)
                    self.stop_highlighting()
                    return
                found_desired_character, space_index = self.reverse_iterate_through_string_for_characters()
                if not found_desired_character:
                    self.current_string = self.current_string[self.selected_index:]
                    self.new_selected_index(0)
                    return
                if space_index == 0:
                    self.current_string = ' ' + self.current_string[self.selected_index:]
                    self.new_selected_index(1)
                    return
                self.current_string = self.current_string[:space_index+1] + self.current_string[self.selected_index:]
                self.new_selected_index(space_index+1)

            case 'CTRL_DELETE':
                if self.currently_highlighting:
                    self.last_edit_time = get_time()
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    self.current_string = self.current_string[:lower_index] + self.current_string[higher_index:]
                    self.new_selected_index(lower_index)
                    self.stop_highlighting()
                    return
                found_desired_character, space_index = self.iterate_through_string_for_character()
                if not found_desired_character:
                    self.current_string = self.current_string[:self.selected_index]
                    self.new_selected_index(len(self.current_string))
                    return
                if self.selected_index + 1 + space_index == len(self.current_string):
                    self.current_string = self.current_string[:self.selected_index] + ' '
                    self.new_selected_index(len(self.current_string) - 1)
                    return
                self.current_string = self.current_string[:self.selected_index] + self.current_string[self.selected_index+space_index:]
                self.new_selected_index(self.selected_index)
            
            case _:
                self.last_edit_time = get_time()
                if self.currently_highlighting:
                    lower_index = min(self.highlighted_index_range)
                    higher_index = max(self.highlighted_index_range)
                    self.current_string = self.current_string[:lower_index] + current_key + self.current_string[higher_index:]
                    self.new_selected_index(lower_index + 1)
                    self.stop_highlighting()
                    return
                if not self.currently_highlighting:
                    self.current_string = self.current_string[:self.selected_index] + current_key + self.current_string[self.selected_index:]
                    self.new_selected_index(self.selected_index + 1)
                    return
    #
    def update_double_click(self, keys_class_instance):
        if keys_class_instance.editor_primary.newly_pressed:
            current_time = get_time()
            if self.currently_selected:
                self.double_clicked = (current_time - self.last_new_primary_click_time) < self.double_click_time
                self.last_new_primary_click_time = current_time
                if self.double_clicked:
                    self.new_selected_index(len(self.current_string))
                    self.highlighted_index_range[0] = 0
                    self.highlighted_index_range[1] = self.selected_index
                    self.update_currently_highlighting()
                    return True
                return False
            else:
                self.last_new_primary_click_time = current_time
                return False
    #
    def reverse_iterate_through_string_for_characters(self):
        space_index = 0
        found_desired_character = False
        first_loop = True
        for index, character in reversed(list(enumerate(self.current_string[:self.selected_index]))):
            if character in self._STOPPING_CHARACTERS:
                if first_loop:
                    continue
                space_index = index
                found_desired_character = True
                break
            first_loop = False
        return found_desired_character, space_index
    #
    def iterate_through_string_for_character(self):
        space_index = 0
        found_desired_character = False
        first_loop = True
        for index, character in enumerate(self.current_string[self.selected_index:]):
            if character in self._STOPPING_CHARACTERS:
                if first_loop:
                    continue
                space_index = index
                found_desired_character = True
                break
            first_loop = False
        return found_desired_character, space_index


# tab, shift tab