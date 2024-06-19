from Code.utilities import point_is_in_ltwh, move_number_to_desired_range, get_text_width
import math


class DynamicInput():
    def __init__(self, allowable_inputs: str, background_ltwh: list[int], background_color: list[float], text_color: list[float], text_pixel_size: int, text_padding: int, allowable_range: list[float | int, float | int] = [-math.inf, math.inf]):
        self.allowable_inputs = allowable_inputs
        self.background_ltwh = background_ltwh
        self.background_color = background_color
        self.text_color = text_color
        self.text_pixel_size = text_pixel_size
        self.text_padding = text_padding
        self.allowable_range = allowable_range
        #
        self.last_new_key = ''
        self.selected_index = 0
        self.currently_selected = False
        self.current_string = '0123456789'
    #
    def update(self, screen_instance, gl_context, keys_class_instance, render_instance, offset_x: int = 0, offset_y: int = 0):
        background_ltwh = self._update(screen_instance, gl_context, keys_class_instance, render_instance, offset_x, offset_y)
        self.draw_blinking_line()
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
            if keys_class_instance.editor_primary.pressed and not cursor_inside_box:
                self.set_current_string_to_range()
                self.currently_selected = False
                return background_ltwh
            if keys_class_instance.editor_primary.pressed and cursor_inside_box:
                self.update_clicked_index(render_instance, keys_class_instance, background_ltwh)
                return background_ltwh
            new_key = self.get_typed_key(keys_class_instance)
            if new_key == self.last_new_key:
                return background_ltwh
            self.last_new_key = new_key
            if new_key is None:
                return background_ltwh
            return background_ltwh
    #
    def set_current_string_to_range(self):
        if self.allowable_range == [-math.inf, math.inf]:
            return
        self.current_string = str(move_number_to_desired_range(self.allowable_range[0], float(self.current_string), self.allowable_range[1]))
    #
    def get_typed_key(self, keys_class_instance):
        current_key = keys_class_instance.keyboard_key_to_character()
        if current_key is None:
            return None
        if current_key in self.allowable_inputs:
            return current_key
        return ''
    #
    def update_clicked_index(self, render_instance, keys_class_instance, background_ltwh):
        current_left = math.floor(background_ltwh[0] + self.text_padding)
        if keys_class_instance.cursor_x_pos.value < current_left:
            self.selected_index = 0
            return
        for index, character in enumerate(self.current_string):
            character_width = get_text_width(render_instance, character, self.text_pixel_size)
            if keys_class_instance.cursor_x_pos.value <= current_left + (character_width / 2):
                self.selected_index = index
                return
            if current_left + (character_width / 2) < keys_class_instance.cursor_x_pos.value <= current_left + character_width:
                self.selected_index = index + 1
                return
            current_left += character_width + self.text_pixel_size
        self.selected_index = len(self.current_string)
    #
    def draw_blinking_line(self):
        pass