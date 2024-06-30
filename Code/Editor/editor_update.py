import math
from Code.utilities import point_is_in_ltwh, move_number_to_desired_range, percent_to_rgba, base10_to_hex, COLORS


def update_header(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
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


def update_footer(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
    #
    # footer bar
    Singleton.footer_ltwh = [0, Screen.height - Singleton.footer_ltwh[3], Screen.width, Singleton.footer_ltwh[3]]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.footer_ltwh, Singleton.footer_color)


def update_palette(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
    #
    # draw palette boundaries
    Singleton.palette_ltwh[3] = Screen.height - Singleton.header_bottom - Singleton.add_color_ltwh[3] - Singleton.footer_ltwh[3] - Singleton.separate_palette_and_add_color_ltwh[3]
    Render.draw_rectangle(Screen, gl_context, (0, Singleton.header_bottom, Singleton.palette_ltwh[2], Singleton.palette_ltwh[3]), Singleton.palette_padding, Singleton.palette_border_color, True, Singleton.palette_background_color, True)
    #
    # draw scroll
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (Singleton.palette_ltwh[2] - Singleton.palette_padding - Singleton.palette_scroll_width, Singleton.palette_ltwh[1] + Singleton.palette_padding, Singleton.palette_scroll_width, Singleton.palette_ltwh[3] - (2 * Singleton.palette_padding)), Singleton.palette_scroll_background_color)
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
            Singleton.add_color_dynamic_inputs[4].current_string = f'{base10_to_hex(red)}{base10_to_hex(green)}{base10_to_hex(blue)}{base10_to_hex(alpha)}'
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


def update_separate_palette_and_add_color(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
    #
    # draw separate palette and add color
    Singleton.separate_palette_and_add_color_ltwh[1] = Singleton.add_color_ltwh[1] - Singleton.separate_palette_and_add_color_ltwh[3]
    Render.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', Singleton.separate_palette_and_add_color_ltwh, Singleton.separate_palette_and_add_color_color)


def update_tools(Singleton, Api, PATH, Screen, gl_context, Render, Time, Keys):
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