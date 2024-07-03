import math
from Code.utilities import point_is_in_ltwh, move_number_to_desired_range, percent_to_rgba, base10_to_hex, add_characters_to_front_of_string, get_time, switch_to_base10, rgba_to_glsl, COLORS


def update_header(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # header banner
    header_ltwh = (0, 0, Screen.width, Singleton.header_height)
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', header_ltwh, Singleton.header_background_color)
    mouse_in_header = point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, header_ltwh)
    if not mouse_in_header:
        Singleton.header_selected = False
        Singleton.header_which_selected = [False for _ in Singleton.header_which_selected]
        Singleton.header_string_selected = ''
        Singleton.header_index_selected = -1
    #
    # header options
    already_highlighted_an_option = False
    for index, string, left, hover_ltwh in zip(Singleton.header_indexes, Singleton.header_strings, Singleton.header_strings_lefts, Singleton.header_hover_ltwh):
        if not already_highlighted_an_option:
            if point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, hover_ltwh):
                already_highlighted_an_option = True
                if Keys.editor_primary.newly_pressed or Singleton.header_selected:
                    Singleton.header_selected = True
                    Singleton.header_which_selected = [False for _ in Singleton.header_which_selected]
                    Singleton.header_which_selected[index] = True
                    Singleton.header_string_selected = Singleton.header_strings[index]
                    Singleton.header_index_selected = index
                if not Singleton.header_which_selected[index]:
                    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', hover_ltwh, Singleton.header_highlight_color)
                if Singleton.header_which_selected[index]:
                    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', hover_ltwh, Singleton.header_selected_color)
        Render.draw_string_of_characters(Screen, gl_context, string, (left, Singleton.header_strings_top), Singleton.header_text_pixel_size, Singleton.header_text_pixel_color)
    #
    # selected header options
    if Singleton.header_selected:
        match Singleton.header_string_selected:
            case 'File':
                pass
            case 'Edit':
                pass
            case 'Options':
                pass
            case 'Objects':
                pass
            case 'Blocks':
                pass
    #
    # header border
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (0, Singleton.header_height, Screen.width, Singleton.header_border_thickness), Singleton.header_border_color)


def update_footer(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # footer bar
    Singleton.footer_ltwh = [0, Screen.height - Singleton.footer_ltwh[3], Screen.width, Singleton.footer_ltwh[3]]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.footer_ltwh, Singleton.footer_color)


def update_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # draw add color background
    Singleton.add_color_ltwh[1] = Singleton.footer_ltwh[1] - Singleton.add_color_ltwh[3]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.add_color_ltwh, Singleton.add_color_background_color)
    #
    # add/remove color button
    Singleton.palette_pressed_add_or_remove_button_this_frame = False
    Singleton.add_color_words_background_ltwh[1] = Singleton.separate_palette_and_add_color_ltwh[1] + Singleton.separate_palette_and_add_color_ltwh[3] + Singleton.palette_padding
    if Singleton.currently_selected_color.color[3] < 1:
        Singleton.add_or_remove_checkerboard_ltwh[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness
        Render.checkerboard(Screen, gl_context, 'black_pixel', Singleton.add_or_remove_checkerboard_ltwh, Singleton.currently_selected_color.checker_color1, Singleton.currently_selected_color.checker_color2, Singleton.add_or_remove_checkerboard_repeat, Singleton.add_or_remove_checkerboard_repeat)
    Render.draw_rectangle(Screen, gl_context, Singleton.add_color_words_background_ltwh, Singleton.add_color_words_border_thickness, Singleton.add_color_words_border_color, True, Singleton.currently_selected_color.color, True)
    # add color
    if not Singleton.currently_selected_color.selected_through_palette:
        Singleton.add_color_words_lt[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness + Singleton.add_color_words_padding
        Render.draw_string_of_characters(Screen, gl_context, Singleton.add_color_words, Singleton.add_color_words_lt, Singleton.add_color_words_text_pixel_size, Singleton.add_color_current_circle_color if Singleton.currently_selected_color.color[3] > 0.5 else COLORS['BLACK'])
        if Keys.editor_primary.newly_pressed and point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, Singleton.add_color_words_background_ltwh) and not Singleton.palette_pressed_add_or_remove_button_this_frame:
            Singleton.palette_pressed_add_or_remove_button_this_frame = True
            Singleton.currently_selected_color.selected_through_palette = True
            if Singleton.currently_selected_color.color in Singleton.palette_colors:
                for index, color in enumerate(Singleton.palette_colors):
                    if Singleton.currently_selected_color.color == color:
                        Singleton.currently_selected_color.palette_index = index
            else:
                Singleton.palette_colors.append(Singleton.currently_selected_color.color)
                Singleton.currently_selected_color.palette_index = len(Singleton.palette_colors) - 1
    # remove color
    if Singleton.currently_selected_color.selected_through_palette:
        Singleton.remove_color_words_lt[1] = Singleton.add_color_words_background_ltwh[1] + Singleton.add_color_words_border_thickness + Singleton.add_color_words_padding
        Render.draw_string_of_characters(Screen, gl_context, Singleton.remove_color_words, Singleton.remove_color_words_lt, Singleton.add_color_words_text_pixel_size, Singleton.add_color_current_circle_color if Singleton.currently_selected_color.color[3] > 0.5 else COLORS['BLACK'])
        if Keys.editor_primary.newly_pressed and point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, Singleton.add_color_words_background_ltwh) and not Singleton.palette_pressed_add_or_remove_button_this_frame:
            for _ in range(1):
                Singleton.palette_pressed_add_or_remove_button_this_frame = True
                del Singleton.palette_colors[Singleton.currently_selected_color.palette_index]
                if len(Singleton.palette_colors) == 0:
                    Singleton.currently_selected_color.palette_index = -1
                    Singleton.currently_selected_color.selected_through_palette = False
                    break
                if Singleton.currently_selected_color.palette_index == len(Singleton.palette_colors):
                    Singleton.currently_selected_color.palette_index -= 1
                    if len(Singleton.palette_colors) > 0:
                        Singleton.currently_selected_color.color = Singleton.palette_colors[Singleton.currently_selected_color.palette_index]
                    break
                Singleton.currently_selected_color.color = Singleton.palette_colors[Singleton.currently_selected_color.palette_index]
    #
    # RGBA spectrum
    color_spectrum_ltwh = Singleton.get_color_spectrum_ltwh()
    Render.rgba_picker(Screen, gl_context, 'black_pixel', color_spectrum_ltwh, Singleton.currently_selected_color.saturation)
    mouse_is_in_spectrum = point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, color_spectrum_ltwh)
    if mouse_is_in_spectrum:
        Cursor.add_cursor_this_frame('cursor_eyedrop')
        if Keys.editor_primary.newly_pressed:
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
        # update text input displaying rgba and hex
        red, green, blue, alpha = [color_component for color_component in percent_to_rgba((Singleton.currently_selected_color.color))]
        Singleton.add_color_dynamic_inputs[0].current_string = str(red)
        Singleton.add_color_dynamic_inputs[1].current_string = str(green)
        Singleton.add_color_dynamic_inputs[2].current_string = str(blue)
        Singleton.add_color_dynamic_inputs[3].current_string = str(alpha)
        Singleton.add_color_dynamic_inputs[4].current_string = f'{add_characters_to_front_of_string(base10_to_hex(red), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(green), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(blue), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(alpha), 2, "0")}'
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
    if mouse_is_in_saturation:
        Cursor.add_cursor_this_frame('cursor_eyedrop')
        if Keys.editor_primary.newly_pressed and not Singleton.add_color_circle_is_held:
            Singleton.add_color_saturation_circle_is_held = True
            Singleton.currently_selected_color.selected_through_palette = False
    if Singleton.add_color_saturation_circle_is_held:
        saturation_x_pos = move_number_to_desired_range(0, (Keys.cursor_x_pos.value - Singleton.add_color_saturation_ltwh[0]), color_spectrum_ltwh[2])
        Singleton.add_color_saturation_circle_relative_x = saturation_x_pos
        Singleton.currently_selected_color.saturation = Singleton.add_color_saturation_circle_relative_x / color_spectrum_ltwh[2]
        Singleton.add_color_saturation_percentage = (saturation_x_pos / color_spectrum_ltwh[2])
        Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
        # update text input displaying rgba and hex
        red, green, blue, alpha = [color_component for color_component in percent_to_rgba((Singleton.currently_selected_color.color))]
        Singleton.add_color_dynamic_inputs[0].current_string = str(red)
        Singleton.add_color_dynamic_inputs[1].current_string = str(green)
        Singleton.add_color_dynamic_inputs[2].current_string = str(blue)
        Singleton.add_color_dynamic_inputs[3].current_string = str(alpha)
        Singleton.add_color_dynamic_inputs[4].current_string = f'{add_characters_to_front_of_string(base10_to_hex(red), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(green), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(blue), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(alpha), 2, "0")}'
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
    if mouse_is_in_alpha:
        Cursor.add_cursor_this_frame('cursor_eyedrop')
        if Keys.editor_primary.newly_pressed and not Singleton.add_color_saturation_circle_is_held:
            Singleton.add_color_alpha_circle_is_held = True
            Singleton.currently_selected_color.selected_through_palette = False
    if Singleton.add_color_alpha_circle_is_held:
        alpha_x_pos = move_number_to_desired_range(0, (Keys.cursor_x_pos.value - Singleton.add_color_alpha_ltwh[0]), color_spectrum_ltwh[2])
        Singleton.add_color_alpha_circle_relative_x = alpha_x_pos
        Singleton.currently_selected_color.alpha = Singleton.add_color_alpha_circle_relative_x / color_spectrum_ltwh[2]
        Singleton.add_color_alpha_percentage = (alpha_x_pos / color_spectrum_ltwh[2])
        Singleton.currently_selected_color.calculate_color(Singleton.add_color_spectrum_x_percentage, Singleton.add_color_spectrum_y_percentage, Singleton.add_color_alpha_percentage)
        # update text input displaying rgba and hex
        red, green, blue, alpha = [color_component for color_component in percent_to_rgba((Singleton.currently_selected_color.color))]
        Singleton.add_color_dynamic_inputs[0].current_string = str(red)
        Singleton.add_color_dynamic_inputs[1].current_string = str(green)
        Singleton.add_color_dynamic_inputs[2].current_string = str(blue)
        Singleton.add_color_dynamic_inputs[3].current_string = str(alpha)
        Singleton.add_color_dynamic_inputs[4].current_string = f'{add_characters_to_front_of_string(base10_to_hex(red), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(green), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(blue), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(alpha), 2, "0")}'
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
    attempt_to_update_selected_color = False
    changed_value_is_rgba = False
    changed_value_is_hex = False
    Singleton.add_color_rgba_updated_this_frame = False
    Singleton.add_color_input_top = spectrum_border_ltwh[1] + spectrum_border_ltwh[3]
    current_character_top = Singleton.add_color_input_top + Singleton.add_color_input_space_between_inputs
    # manage tab / shift tab
    initial_move_down = (Keys.editor_tab.newly_pressed and not Keys.editor_shift.pressed)
    initial_move_up = (Keys.editor_tab.newly_pressed and Keys.editor_shift.newly_pressed) or (Keys.editor_tab.newly_pressed and Keys.editor_shift.pressed) or (Keys.editor_tab.pressed and Keys.editor_shift.newly_pressed)
    if initial_move_down or initial_move_up:
        Singleton.add_color_input_moving_down = True if initial_move_down else False
        Singleton.add_color_input_initial_fast_move = get_time()
    if Keys.editor_tab.pressed:
        current_time = get_time()
        moving_this_frame = (initial_move_down or initial_move_up or ((current_time - Singleton.add_color_input_initial_fast_move > Singleton.add_color_input_time_before_fast_move) and (current_time - Singleton.add_color_input_last_move_time > Singleton.add_color_input_time_between_moves)))
        if moving_this_frame:
            Singleton.add_color_input_last_move_time = get_time()
            old_selected_index = -1
            for index, text_input in enumerate(Singleton.add_color_dynamic_inputs):
                if text_input.currently_selected:
                    attempt_to_update_selected_color = True
                    if 0 <= index <= 3:
                        changed_value_is_rgba = True
                    if index == 4:
                        changed_value_is_hex = True
                    old_selected_index = index
                    text_input.deselect_box()
            if old_selected_index != -1:
                if Singleton.add_color_input_moving_down:
                    newly_selected_index = (old_selected_index + 1) % len(Singleton.add_color_inputs)
                if not Singleton.add_color_input_moving_down:
                    newly_selected_index = (old_selected_index - 1) % len(Singleton.add_color_inputs)
                Singleton.add_color_dynamic_inputs[newly_selected_index].currently_selected = True
                Singleton.add_color_dynamic_inputs[newly_selected_index].highlighted_index_range = [0, len(Singleton.add_color_dynamic_inputs[newly_selected_index].current_string)]
                Singleton.add_color_dynamic_inputs[newly_selected_index].currently_highlighting = True
                Singleton.add_color_dynamic_inputs[newly_selected_index].selected_index = len(Singleton.add_color_dynamic_inputs[newly_selected_index].current_string)
    # update text input objects
    text_offset_y = -Singleton.add_color_dynamic_inputs[0].text_padding / 2
    for index, input_character in enumerate(Singleton.add_color_inputs[:4]):
        Render.draw_string_of_characters(Screen, gl_context, input_character, [Singleton.add_color_input_color_equals_input_left[0], current_character_top], Singleton.add_color_input_text_pixel_size, Singleton.add_color_input_inputs_and_equals_color)
        Render.draw_string_of_characters(Screen, gl_context, '=', [Singleton.add_color_input_color_equals_input_left[1], current_character_top], Singleton.add_color_input_text_pixel_size, Singleton.add_color_input_inputs_and_equals_color)
        Singleton.add_color_dynamic_inputs[index].background_ltwh[1] = current_character_top
        Singleton.add_color_dynamic_inputs[index].update(Screen, gl_context, Keys, Render, offset_y=text_offset_y)
        if not attempt_to_update_selected_color:
            attempt_to_update_selected_color = Singleton.add_color_dynamic_inputs[index].should_update_spectrum
            if attempt_to_update_selected_color:
                changed_value_is_rgba = True
        current_character_top += Singleton.add_color_input_single_input_height
    # HEX
    index, characters = 4, Singleton.add_color_inputs[4]
    Render.draw_string_of_characters(Screen, gl_context, characters, [Singleton.add_color_input_color_equals_input_left[0], current_character_top], Singleton.add_color_input_text_pixel_size, Singleton.add_color_input_inputs_and_equals_color)
    Singleton.add_color_dynamic_inputs[index].background_ltwh[1] = current_character_top
    Singleton.add_color_dynamic_inputs[index].update(Screen, gl_context, Keys, Render, offset_y=text_offset_y)
    if not attempt_to_update_selected_color:
        attempt_to_update_selected_color = Singleton.add_color_dynamic_inputs[index].should_update_spectrum
        if attempt_to_update_selected_color:
            changed_value_is_hex = True
    # update currently selected color
    if attempt_to_update_selected_color:
        Singleton.currently_selected_color.selected_through_palette = False
        change_spectrum_to_new_color = False
        if changed_value_is_rgba:
            all_are_valid = True
            for text_input in Singleton.add_color_dynamic_inputs[:4]:
                if not text_input.is_valid():
                    all_are_valid = False
            if all_are_valid:
                red = round(float(Singleton.add_color_dynamic_inputs[0].current_string))
                green = round(float(Singleton.add_color_dynamic_inputs[1].current_string))
                blue = round(float(Singleton.add_color_dynamic_inputs[2].current_string))
                alpha = round(float(Singleton.add_color_dynamic_inputs[3].current_string))
                new_color = rgba_to_glsl((red, green, blue, alpha))
                Singleton.add_color_dynamic_inputs[4].current_string = f'{add_characters_to_front_of_string(base10_to_hex(red), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(green), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(blue), 2, "0")}{add_characters_to_front_of_string(base10_to_hex(alpha), 2, "0")}'
                change_spectrum_to_new_color = True
        if changed_value_is_hex:
            if Singleton.add_color_dynamic_inputs[4].is_valid():
                hex_string = add_characters_to_front_of_string(Singleton.add_color_dynamic_inputs[4].current_string, 8, '0')
                red = switch_to_base10(hex_string[0:2], 16)
                green = switch_to_base10(hex_string[2:4], 16)
                blue = switch_to_base10(hex_string[4:6], 16)
                alpha = switch_to_base10(hex_string[6:8], 16)
                new_color = rgba_to_glsl((red, green, blue, alpha))
                Singleton.add_color_dynamic_inputs[0].current_string = str(red)
                Singleton.add_color_dynamic_inputs[1].current_string = str(green)
                Singleton.add_color_dynamic_inputs[2].current_string = str(blue)
                Singleton.add_color_dynamic_inputs[3].current_string = str(alpha)
                change_spectrum_to_new_color = True
        # change to new color
        if change_spectrum_to_new_color:
            # update spectrum based on palette selection
            Singleton.add_color_spectrum_x_percentage, Singleton.add_color_saturation_percentage, Singleton.add_color_spectrum_y_percentage = Singleton.currently_selected_color.rgb_to_hsl(new_color)
            Singleton.add_color_alpha_percentage = new_color[3]
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


def update_separate_palette_and_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # draw separate palette and add color
    Singleton.separate_palette_and_add_color_ltwh[1] = Singleton.add_color_ltwh[1] - Singleton.separate_palette_and_add_color_ltwh[3]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.separate_palette_and_add_color_ltwh, Singleton.separate_palette_and_add_color_color)


def update_tools(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys, Cursor):
    #
    # draw bool bar background
    Singleton.tool_bar_ltwh[0] = Screen.width - Singleton.tool_bar_ltwh[2]
    Singleton.tool_bar_ltwh[3] = Singleton.footer_ltwh[1] - Singleton.header_bottom
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.tool_bar_ltwh, Singleton.tool_bar_color)
    #
    # draw tools
    drawn_glowing_tool_this_frame = False
    for tool_name, tool_attributes in Singleton.tool_bar_tools_dict.items():
        tool_attributes[0][0] = Singleton.tool_bar_ltwh[0] + Singleton.tool_bar_padding
        if tool_attributes[1] and not drawn_glowing_tool_this_frame:
            Render.basic_outline_ltwh(Screen, gl_context, tool_name, tool_attributes[0], Singleton.tool_bar_glow_color, Singleton.tool_bar_outline_pixels)
            drawn_glowing_tool_this_frame = True
        if Keys.editor_primary.newly_pressed:
            if point_is_in_ltwh(Keys.cursor_x_pos.value, Keys.cursor_y_pos.value, tool_attributes[0]):
                Singleton.tool_bar_tools_dict = {key: [value[0], False if key != tool_name else True] for key, value in Singleton.tool_bar_tools_dict.items()}
        Render.basic_rect_ltwh_to_quad(Screen, gl_context, tool_name, tool_attributes[0])