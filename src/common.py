import math
import os
from logging import warning
from src.config import WindowCnf
import pygame
import pygame as pg

CWDIR = os.getcwd() + "/"

# INIT GAME ==============================================
pygame.init()  # initiate pygame

print("INIT GAME VARS")
VERSION = "0.1a"
WINDOW_SIZE = list(map(int, WindowCnf.WindowSize))
FULLSCREEN = WindowCnf.FullScreen
desktop_size = pygame.display.get_desktop_sizes()[0]
if FULLSCREEN:
    WINDOW_SIZE = desktop_size

WSIZE = WINDOW_SIZE

FPS = 30

pygame.display.set_caption('GraphiCode')

# screen_ = pygame.display.set_mode(WINDOW_SIZE, flags=pygame.SCALED, vsync=2)
screen_ = pygame.display.set_mode(WINDOW_SIZE, vsync=2)
display_ = pygame.Surface(WINDOW_SIZE)

NUM_KEYS = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8, pg.K_9, pg.K_0]

# COLORS ==================================================================
colors = ['#CD5C5C', '#F08080', '#FA8072', '#E9967A', '#FFA07A', '#DC143C', '#FF0000', '#B22222', '#8B0000', '#FFC0CB',
          '#FFB6C1', '#FF69B4', '#FF1493', '#C71585', '#DB7093', '#FFA07A', '#FF7F50', '#FF6347', '#FF4500', '#FF8C00',
          '#FFA500', '#FFD700', '#FFFF00', '#FFFFE0', '#FFFACD', '#FAFAD2', '#FFEFD5', '#FFE4B5', '#FFDAB9', '#EEE8AA',
          '#F0E68C', '#BDB76B', '#E6E6FA', '#D8BFD8', '#DDA0DD', '#EE82EE', '#DA70D6', '#FF00FF', '#FF00FF', '#BA55D3',
          '#9370DB', '#8A2BE2', '#9400D3', '#9932CC', '#8B008B', '#800080', '#4B0082', '#6A5ACD', '#483D8B', '#FFF8DC',
          '#FFEBCD', '#FFE4C4', '#FFDEAD', '#F5DEB3', '#DEB887', '#D2B48C', '#BC8F8F', '#F4A460', '#DAA520', '#B8860B',
          '#CD853F', '#D2691E', '#8B4513', '#A0522D', '#A52A2A', '#800000', '#000000', '#808080', '#C0C0C0', '#FFFFFF',
          '#FF00FF', '#800080', '#FF0000', '#800000', '#FFFF00', '#808000', '#00FF00', '#008000', '#00FFFF', '#008080',
          '#0000FF', '#000080', '#ADFF2F', '#7FFF00', '#7CFC00', '#00FF00', '#32CD32', '#98FB98', '#90EE90', '#00FA9A',
          '#00FF7F', '#3CB371', '#2E8B57', '#228B22', '#008000', '#006400', '#9ACD32', '#6B8E23', '#808000', '#556B2F',
          '#66CDAA', '#8FBC8F', '#20B2AA', '#008B8B', '#008080', '#00FFFF', '#00FFFF', '#E0FFFF', '#AFEEEE', '#7FFFD4',
          '#40E0D0', '#48D1CC', '#00CED1', '#5F9EA0', '#4682B4', '#B0C4DE', '#B0E0E6', '#ADD8E6', '#87CEEB', '#87CEFA',
          '#00BFFF', '#1E90FF', '#6495ED', '#7B68EE', '#4169E1', '#0000FF', '#0000CD', '#00008B', '#000080', '#191970',
          '#FFFFFF', '#FFFAFA', '#F0FFF0', '#F5FFFA', '#F0FFFF', '#F0F8FF', '#F8F8FF', '#F5F5F5', '#FFF5EE', '#F5F5DC',
          '#FDF5E6', '#FFFAF0', '#FFFFF0', '#FAEBD7', '#FAF0E6', '#FFF0F5', '#FFE4E1', '#DCDCDC', '#D3D3D3', '#D3D3D3',
          '#C0C0C0', '#A9A9A9', '#A9A9A9', '#808080', '#808080', '#696969', '#696969', '#778899', '#778899', '#708090',
          '#708090', '#2F4F4F', '#2F4F4F', '#000000']

# SAVE_DATA =================================================
# class SavedObject:
# not_save_vars = {"", }
# is_not_saving = False
#
# def get_vars(self, _dict=None):
#     # print(self.not_save_vars)
#     if _dict is None:
#         _dict = self.__dict__.copy()
#     _dict["__class__"] = self.__class__
#     for key, value in list(_dict.items()):
#         if key in self.not_save_vars:
#             _dict.pop(key)
#         elif isinstance(value, SavedObject):
#             if not value.is_not_saving:
#                 _dict[key] = value.get_vars()
#             else:
#                 _dict.pop(key)
#         elif isinstance(value, pg.Surface) or (
#                 isinstance(value, (list, tuple)) and value and isinstance(value[0], pg.Surface)):
#             warning(f"Не контроллируемый {key}: {value}, удален из сохранения!")
#             _dict.pop(key)
#         elif isinstance(value, (list, tuple)) and value and isinstance(value[0], SavedObject):
#             warning(f"Не контроллируемый списочный SavedObject {key}: {value}, удален из сохранения!")
#             _dict.pop(key)
#     # print(self.__class__, d)
#     # pickle.dumps(d)
#     return _dict
#
# def set_vars(self, vrs, _dict=None):
#     if _dict is None:
#         _dict = self.__dict__.copy()
#     if "__class__" in vrs:
#         vrs.pop("__class__")
#     for var_name, var_value in vrs.items():
#         if isinstance(var_value, dict) and var_value.get("__class__"):
#             _dict[var_name].set_vars(var_value)
#         else:
#             _dict[var_name] = var_value
