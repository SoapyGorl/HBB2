from Code.utilities import point_is_in_ltwh


class DynamicInput():
    def __init__(self, allowable_inputs: str, background_ltwh: list[int], background_color: list[float], text_color: list[float], text_pixel_size: int):
        self.allowable_inputs = allowable_inputs
        self.background_ltwh = background_ltwh
        self.background_color = background_color
        self.text_color = text_color
        self.text_pixel_size = text_pixel_size
        #
        self.selected_index = 0
        self.currently_selected = False
        self.current_value = ''
    #
    def update(self, screen_instance, gl_context, keys_class_instance, render_instance):
        render_instance.basic_rect_ltwh_with_color_to_quad(screen_instance, gl_context, 'black_pixel', self.background_ltwh, self.background_color)
        if not self.currently_selected:
            if not keys_class_instance.editor_primary:
                return
            clicked_inside_box = point_is_in_ltwh(keys_class_instance.cursor_x_pos.value, keys_class_instance.cursor_y_pos.value, self.background_ltwh)
        else:
            new_key = self.get_typed_key()
    #
    def get_typed_key(self, keys_class_instance):
        current_key = keys_class_instance.keyboard_key_to_character()
        if current_key in self.allowable_inputs:
            return current_key
        else: 
            return ''