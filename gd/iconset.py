from .graphics.colors import colors

class IconSet:
    def __init__(self, **options):
        self.options = options
    
    def __str__(self):
        glow_outline = 'On' if self.has_glow_outline() else 'Off'
        res = f'[gd.IconSet]\n[Icons]\n[Main:{self.main}][Type:{self.main_type}]\n[Cube:{self.cube}]\n[Ship:{self.ship}]\n[Ball:{self.ball}]\n[Ufo:{self.ufo}]\n[Wave:{self.wave}]\n[Robot:{self.robot}]\n[Spider:{self.spider}]\n[Colors]\n[Color_1:{self.color_1.to_hex()}]\n[Color_2:{self.color_2.to_hex()}]\n[Glow_Outline:{glow_outline}]'
        return res
    
    def __repr__(self):
        ret = f'<gd.IconSet: color_1={repr(self.color_1)}, color_2={repr(self.color_2)}>'
        return ret

    @property
    def main(self):
        return self.options.get('main_icon')
    @property
    def color_1(self):
        return get_color(self, 'color_1')
    @property
    def color_2(self):
        return get_color(self, 'color_2')
    @property
    def main_type(self):
        return self.options.get('main_icon_type')
    @property
    def cube(self):
        return self.options.get('icon_cube')
    @property
    def ship(self):
        return self.options.get('icon_ship')
    @property
    def ball(self):
        return self.options.get('icon_ball')
    @property
    def ufo(self):
        return self.options.get('icon_ufo')
    @property
    def wave(self):
        return self.options.get('icon_wave')
    @property
    def robot(self):
        return self.options.get('icon_robot')
    @property
    def spider(self):
        return self.options.get('icon_spider')
    
    def has_glow_outline(self):
        return self.options.get('has_glow_outline')
    
    def get_colors(self):
        return self.color_1, self.color_2

def get_color(obj: IconSet, strcolor: str):
    try:
        return colors[obj.options.get(strcolor)]
    except ValueError:
        return None