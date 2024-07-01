from array import array
import math
from Code.utilities import atan2, get_text_height, get_text_width
import pygame
import moderngl


def initialize_display():
    Screen = ScreenObject()
    #
    gl_context = moderngl.create_context()
    gl_context.enable(moderngl.BLEND)
    Render = RenderObjects(gl_context)
    #
    return Screen, Render, gl_context


class ScreenObject():
    def __init__(self):
        self.ACCEPTABLE_WIDTH_RANGE = [650, 10000]
        self.ACCEPTABLE_HEIGHT_RANGE = [650, 10000]
        self.width = 1000
        self.height = 700
        self.aspect = self.width / self.height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
        self.display = pygame.Surface((self.width, self.height))
    #
    def update_aspect(self):
        self.aspect = self.width / self.height
    #
    def update(self):
        pygame.display.flip()


class RenderableObject():
    def __init__(self, Screen: ScreenObject, texture, width, height, rotation):
        self.TEXTURE = texture
        self.ORIGINAL_WIDTH = width
        self.ORIGINAL_HEIGHT = height
        self.rotation = rotation
        #
        topleft_x = -1.0
        topleft_y = 1.0
        topright_x = topleft_x + ((2 * self.ORIGINAL_WIDTH) / Screen.width)
        bottomleft_y = topleft_y - ((2 * self.ORIGINAL_HEIGHT) / Screen.height)
        center_x = (topleft_x + topright_x) / 2
        center_y = (topleft_y + bottomleft_y) / 2
        self.ORIGINAL_HYPOTNUSE = math.sqrt(abs(topleft_x - center_x)**2 + abs(topleft_y - center_y) / 2)
        #
        topleft_rot = atan2(-abs(center_x - topleft_x), abs(center_y - topleft_y))
        topright_rot = atan2(abs(center_x - topright_x), abs(center_y - topleft_y))
        bottomleft_rot = atan2(abs(center_x - topleft_x), -abs(center_y - bottomleft_y))
        bottomright_rot = atan2(-abs(center_x - topright_x), -abs(center_y - bottomleft_y))
        self.ORIGINAL_ROTATIONS = [topleft_rot, topright_rot, bottomleft_rot, bottomright_rot]


class RenderObjects():
    def __init__(self, gl_context):
        self.programs = {}
        self.get_programs(gl_context) # 'program_name': program
        self.renderable_objects = {} # 'object_name': RenderableObject
    #
    def get_programs(self, gl_context):
        self.programs['basic_rect'] = DrawBasicRect(gl_context)
        self.programs['rotation_rect'] = DrawRotationRect(gl_context)
        self.programs['basic_image_with_color'] = DrawImageWithColor(gl_context)
        self.programs['basic_rect_with_color'] = DrawBasicRectWithVariableColor(gl_context)
        self.programs['basic_rect_glow'] = DrawBasicRectGlow(gl_context)
        self.programs['basic_rect_circle_glow'] = DrawBasicRectCircleGlow(gl_context)
        self.programs['basic_outline'] = DrawBasicOutline(gl_context)
        self.programs['RGBA_picker'] = DrawRGBAPicker(gl_context)
        self.programs['spectrum_x'] = DrawSpectrumX(gl_context)
        self.programs['checkerboard'] = DrawCheckerboard(gl_context)
        self.programs['text'] = DrawText(gl_context)
    #
    def add_moderngl_texture_to_renderable_objects_dict(self, Screen: ScreenObject, gl_context, path, name):
        pygame_image = pygame.image.load(path).convert_alpha()
        width, height = pygame_image.get_size()
        texture = gl_context.texture((width, height), 4)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        texture.swizzle = 'BGRA'
        texture.write(pygame_image.get_view('1'))
        rotation = 0
        self.renderable_objects[name] = RenderableObject(Screen, texture, width, height, rotation)
    #
    def remove_moderngl_texture_from_renderable_objects_dict(self, name):
        self.renderable_objects[name].TEXTURE.release()
        del self.renderable_objects[name]
    #
    def basic_rect_ltwh_to_quad(self, Screen: ScreenObject, gl_context, object_name, ltwh):
        # 'basic_rect', DrawBasicRect
        program = self.programs['basic_rect'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def rotation_rect_ltwhr_to_quad(self, Screen: ScreenObject, gl_context, object_name, ltwhr):
        # 'rotation_rect', DrawRotationRect
        program = self.programs['rotation_rect'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwhr[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwhr[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwhr[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwhr[3]) / Screen.height)
        program['rotation'] = math.radians(ltwhr[4])
        program['offset_x'] = (topleft_x + topright_x) / 2
        program['offset_y'] = (topleft_y + bottomleft_y) / 2
        program['aspect'] = Screen.aspect
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def basic_rect_ltwh_image_with_color(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba):
        # 'basic_image_with_color', DrawImageWithColor
        program = self.programs['basic_image_with_color'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red'] = rgba[0]
        program['green'] = rgba[1]
        program['blue'] = rgba[2]
        program['alpha'] = rgba[3]
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def basic_rect_ltwh_with_color_to_quad(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba):
        # 'basic_rect_with_color', DrawBasicRectWithVariableColor
        program = self.programs['basic_rect_with_color'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red'] = rgba[0]
        program['green'] = rgba[1]
        program['blue'] = rgba[2]
        program['alpha'] = rgba[3]
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def basic_rect_ltwh_glow(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba, glowing_pixels):
        # 'basic_rect_glow', DrawBasicRectGlow
        new_ltwh = [ltwh[0] - glowing_pixels, ltwh[1] - glowing_pixels, ltwh[2] + (2 * glowing_pixels), ltwh[3] + (2 * glowing_pixels)]
        program = self.programs['basic_rect_glow'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * new_ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * new_ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * new_ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * new_ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red'] = rgba[0]
        program['green'] = rgba[1]
        program['blue'] = rgba[2]
        program['glowing_pixels'] = abs(1 - (ltwh[2] / new_ltwh[2]))
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def basic_rect_circle_ltwh_glow(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba, glowing_pixels, brightness):
        # 'basic_rect_circle_glow', DrawBasicRectCircleGlow
        new_ltwh = [ltwh[0] - glowing_pixels, ltwh[1] - glowing_pixels, ltwh[2] + (2 * glowing_pixels), ltwh[3] + (2 * glowing_pixels)]
        program = self.programs['basic_rect_circle_glow'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * new_ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * new_ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * new_ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * new_ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red'] = rgba[0]
        program['green'] = rgba[1]
        program['blue'] = rgba[2]
        program['brightness'] = brightness
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def basic_outline_ltwh(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba, outline_pixels):
        # 'basic_outline', DrawBasicOutline
        new_ltwh = [ltwh[0] - outline_pixels, ltwh[1] - outline_pixels, ltwh[2] + (2 * outline_pixels), ltwh[3] + (2 * outline_pixels)]
        program = self.programs['basic_outline'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * new_ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * new_ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * new_ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * new_ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red'] = rgba[0]
        program['green'] = rgba[1]
        program['blue'] = rgba[2]
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def rgba_picker(self, Screen: ScreenObject, gl_context, object_name, ltwh, saturation):
        # 'RGBA_picker', DrawRGBAPicker
        width = ltwh[2] / 6
        height = ltwh[3] / 2
        for left_index in range(6):
            left = ltwh[0] + (left_index * width)
            for top_index in range(2):
                top = ltwh[1] + (top_index * height)
                key = f'{str(left_index)}_{str(top_index)}'
                program = self.programs['RGBA_picker'].PROGRAMS[key]
                renderable_object = self.renderable_objects[object_name]
                topleft_x = (-1.0 + ((2 * left) / Screen.width)) * Screen.aspect
                topleft_y = 1.0 - ((2 * top) / Screen.height)
                topright_x = topleft_x + ((2 * width * Screen.aspect) / Screen.width)
                bottomleft_y = topleft_y - ((2 * height) / Screen.height)
                program['aspect'] = Screen.aspect
                program['saturation'] = saturation
                quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
                renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
                renderable_object.TEXTURE.use(0)
                renderer.render(mode=moderngl.TRIANGLE_STRIP)
                quads.release()
                renderer.release()
    #
    def spectrum_x(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba1, rgba2):
        # 'spectrum_x', DrawSpectrumX
        program = self.programs['spectrum_x'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red1'] = rgba1[0]
        program['green1'] = rgba1[1]
        program['blue1'] = rgba1[2]
        program['alpha1'] = rgba1[3]
        program['red2'] = rgba2[0]
        program['green2'] = rgba2[1]
        program['blue2'] = rgba2[2]
        program['alpha2'] = rgba2[3]
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def checkerboard(self, Screen: ScreenObject, gl_context, object_name, ltwh, rgba1, rgba2, repeat_x, repeat_y):
        # 'checkerboard', DrawCheckerboard
        program = self.programs['checkerboard'].program
        renderable_object = self.renderable_objects[object_name]
        topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
        topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
        topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
        bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
        program['aspect'] = Screen.aspect
        program['red1'] = rgba1[0]
        program['green1'] = rgba1[1]
        program['blue1'] = rgba1[2]
        program['alpha1'] = rgba1[3]
        program['red2'] = rgba2[0]
        program['green2'] = rgba2[1]
        program['blue2'] = rgba2[2]
        program['alpha2'] = rgba2[3]
        program['two_tiles_x'] = 2 / (ltwh[2] / repeat_x)
        program['two_tiles_y'] = 2 / (ltwh[3] / repeat_y)
        quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
        renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
        renderable_object.TEXTURE.use(0)
        renderer.render(mode=moderngl.TRIANGLE_STRIP)
        quads.release()
        renderer.release()
    #
    def draw_string_of_characters(self, Screen: ScreenObject, gl_context, string, lt, text_pixel_size, rgba):
        # 'text', DrawText
        ltwh = [lt[0], lt[1], 0, get_text_height(text_pixel_size)]
        for character in string:
            ltwh[2] = get_text_width(self, character, text_pixel_size)
            program = self.programs['text'].program
            renderable_object = self.renderable_objects[character]
            topleft_x = (-1.0 + ((2 * ltwh[0]) / Screen.width)) * Screen.aspect
            topleft_y = 1.0 - ((2 * ltwh[1]) / Screen.height)
            topright_x = topleft_x + ((2 * ltwh[2] * Screen.aspect) / Screen.width)
            bottomleft_y = topleft_y - ((2 * ltwh[3]) / Screen.height)
            program['aspect'] = Screen.aspect
            program['red'] = rgba[0]
            program['green'] = rgba[1]
            program['blue'] = rgba[2]
            program['alpha'] = rgba[3]
            quads = gl_context.buffer(data=array('f', [topleft_x, topleft_y, 0.0, 0.0, topright_x, topleft_y, 1.0, 0.0, topleft_x, bottomleft_y, 0.0, 1.0, topright_x, bottomleft_y, 1.0, 1.0,]))
            renderer = gl_context.vertex_array(program, [(quads, '2f 2f', 'vert', 'texcoord')])
            renderable_object.TEXTURE.use(0)
            renderer.render(mode=moderngl.TRIANGLE_STRIP)
            quads.release()
            renderer.release()
            ltwh[0] += ltwh[2] + text_pixel_size
    #
    def draw_rectangle(self, Screen: ScreenObject, gl_context, ltwh, border_thickness, border_color, coloring_border, inner_color, coloring_inside): # rectangle with border
        if coloring_border:
            self.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (ltwh[0], ltwh[1], ltwh[2], border_thickness), border_color)
            self.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (ltwh[0], ltwh[1] + border_thickness, border_thickness, ltwh[3] - border_thickness), border_color)
            self.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (ltwh[0] + ltwh[2] - border_thickness, ltwh[1] + border_thickness, border_thickness, ltwh[3] - border_thickness), border_color)
            self.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (ltwh[0] + border_thickness, ltwh[1] + ltwh[3] - border_thickness, ltwh[2] - (2 * border_thickness), border_thickness), border_color)
        if coloring_inside:
            self.basic_rect_ltwh_with_color_to_quad(Screen, gl_context, 'blank_pixel', (ltwh[0] + border_thickness, ltwh[1] + border_thickness, ltwh[2] - (2 * border_thickness), ltwh[3] - (2 * border_thickness)), inner_color)
    #
    @staticmethod
    def clear_buffer(gl_context):
        gl_context.clear()


class DrawBasicRect():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = texture(tex, uvs);
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawRotationRect():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float rotation;
        uniform float offset_x;
        uniform float offset_y;
        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            vec2 sample_pos = vec2(
            offset_x + ((vert.x - offset_x) * cos(rotation)) - ((vert.y - offset_y) * sin(rotation)), 
            offset_y + ((vert.x - offset_x) * sin(rotation)) + ((vert.y - offset_y) * cos(rotation))
            );
            sample_pos.x /= aspect;
            gl_Position = vec4(sample_pos, 0.0, 1.0);
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(texture(tex, uvs).rgba);
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawBasicRectWithVariableColor():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;
        uniform float alpha;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            texture(tex, uvs).a + alpha
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawImageWithColor():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;
        uniform float alpha;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            texture(tex, uvs).a * alpha
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawText():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;
        uniform float alpha;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            texture(tex, uvs).a * alpha
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawBasicRectGlow():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;
        uniform float glowing_pixels;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            min(abs((abs(0.5 - uvs.x) * 2) - 1), abs((abs(0.5 - uvs.y) * 2) - 1)) * (1 / glowing_pixels)
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawBasicRectCircleGlow():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;
        uniform float brightness;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            abs(clamp(pow(pow(2*abs(uvs.x - 0.5), 2) + pow(2*abs(uvs.y - 0.5), 2), 0.5), 0 , 1) - 1) * brightness
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawBasicOutline():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red;
        uniform float green;
        uniform float blue;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            texture(tex, uvs).r + red, 
            texture(tex, uvs).g + green, 
            texture(tex, uvs).b + blue, 
            texture(tex, uvs).a
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawRGBAPicker():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADERS = {
        '0_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 1;
            float green = 1 - ((1 - uvs.x) * uvs.y);
            float blue = (1 - uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '1_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 1 - (uvs.x * uvs.y);
            float green = 1;
            float blue = (1 - uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '2_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = (1 - uvs.y);
            float green = 1;
            float blue = 1 - ((1 - uvs.x) * uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '3_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = (1 - uvs.y);
            float green = 1 - (uvs.x * uvs.y);
            float blue = 1;
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '4_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 1 - ((1 - uvs.x) * uvs.y);
            float green = (1 - uvs.y);
            float blue = 1;
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '5_0': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 1;
            float green = (1 - uvs.y);
            float blue = 1 - (uvs.x * uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '0_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = (1 - uvs.y);
            float green = uvs.x * (1 - uvs.y);
            float blue = 0;
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '1_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = (1-uvs.x) * (1-uvs.y);
            float green = (1 - uvs.y);
            float blue = 0;
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '2_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 0;
            float green = (1 - uvs.y);
            float blue = uvs.x * (1 - uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '3_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = 0;
            float green = (1-uvs.x) * (1-uvs.y);
            float blue = (1 - uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '4_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = uvs.x * (1 - uvs.y);
            float green = 0;
            float blue = (1 - uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        ''',

        '5_1': 
        '''
        #version 330 core

        uniform sampler2D tex;
        uniform float saturation;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float red = (1 - uvs.y);
            float green = 0;
            float blue = (1-uvs.x) * (1-uvs.y);
            float max_color = max(max(red, green), blue);
            float min_color = min(min(red, green), blue);
            float middle_color = ((max_color - min_color) / 2) + min_color;
            float adjustment = (middle_color * (1 - saturation));
            red = (red * saturation) + adjustment;
            green = (green * saturation) + adjustment;
            blue = (blue * saturation) + adjustment;
            f_color = vec4(red, green, blue, texture(tex, uvs).a);
        }
        '''
        }
        self.PROGRAMS = {
        '0_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['0_0']),
        '1_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['1_0']),
        '2_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['2_0']),
        '3_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['3_0']),
        '4_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['4_0']),
        '5_0':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['5_0']),
        '0_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['0_1']),
        '1_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['1_1']),
        '2_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['2_1']),
        '3_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['3_1']),
        '4_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['4_1']),
        '5_1':  gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADERS['5_1'])
        }


class DrawSpectrumX():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red1;
        uniform float green1;
        uniform float blue1;
        uniform float alpha1;
        uniform float red2;
        uniform float green2;
        uniform float blue2;
        uniform float alpha2;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            f_color = vec4(
            ((1 - uvs.x) * red1) + (uvs.x * red2), 
            ((1 - uvs.x) * green1) + (uvs.x * green2), 
            ((1 - uvs.x) * blue1) + (uvs.x * blue2), 
            ((1 - uvs.x) * alpha1) + (uvs.x * alpha2)
            );
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)


class DrawCheckerboard():
    def __init__(self, gl_context):
        self.VERTICE_SHADER = '''
        #version 330 core

        uniform float aspect;

        in vec2 vert;
        in vec2 texcoord;
        out vec2 uvs;

        void main() {
            uvs = texcoord;
            gl_Position = vec4(
            vert.x / aspect, 
            vert.y, 0.0, 1.0
            );
        }
        '''
        self.FRAGMENT_SHADER = '''
        #version 330 core

        uniform sampler2D tex;
        uniform float red1;
        uniform float green1;
        uniform float blue1;
        uniform float alpha1;
        uniform float red2;
        uniform float green2;
        uniform float blue2;
        uniform float alpha2;
        uniform float two_tiles_x;
        uniform float two_tiles_y;

        in vec2 uvs;
        out vec4 f_color;

        void main() {
            float one_tile_x = two_tiles_x / 2;
            float one_tile_y = two_tiles_y / 2;
            f_color = vec4(red1, green1, blue1, alpha1);
            if ((mod(uvs.x, two_tiles_x) < one_tile_x) ^^ (mod(uvs.y, two_tiles_y) < one_tile_y)) {
                f_color = vec4(red2, green2, blue2, alpha2);
            }
        }
        '''
        self.program = gl_context.program(vertex_shader = self.VERTICE_SHADER, fragment_shader = self.FRAGMENT_SHADER)