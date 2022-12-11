import os
import pickle
from logging import warning
from typing import Union, List

from units.common import VERSION

CWDIR = os.getcwd() + "/"
SAVES_PATH = CWDIR + "saves/"

if not os.path.exists(SAVES_PATH):
    os.mkdir(SAVES_PATH)


class SavedObject:
    save_vars = set()
    is_saving = True

    def get_vars(self, _dict=None):
        # print(self.not_save_vars)
        if _dict is None:
            _dict = self.__dict__.copy()
        var_dict = {}
        var_dict["__class__"] = self.__class__
        for key, value in list(_dict.items()):
            if key not in self.save_vars:
                if isinstance(value, (SavedObject, SavedObjectList)):
                    if not value.is_saving:
                        var_dict[key] = value.get_vars()
                else:
                    var_dict[key] = value
        return var_dict

    def set_vars(self, vrs, _dict=None):
        if _dict is None:
            _dict = self.__dict__.copy()
        if "__class__" in vrs:
            vrs.pop("__class__")
        for var_name, var_value in vrs.items():
            if isinstance(var_value, dict) and var_value.get("__class__"):
                _dict[var_name].set_vars(var_value)
            elif isinstance(var_value, SavedObjectList):
                _dict[var_name].set_vars(var_value)


class SavedObjectList(list):
    def __init__(self, *args, init_vars_object: Union[List[SavedObject], None] = None, **kwargs_object):
        super().__init__(*args)
        self.init_vars_object = init_vars_object if init_vars_object is not None else []
        self.kwargs_object = kwargs_object

    def get_vars(self, _dict=None):
        vrs = []
        for el in self:
            vrs.append(el.get_vars())
        return vrs

    def set_vars(self, vrs, _dict=None):
        self.clear()
        if _dict is None:
            _dict = self.__dict__.copy()
        for var_object in vrs:
            init_vars_object = [var_object[var_name] for var_name in self.init_vars_object]
            self.append(var_object["__class__"](*init_vars_object, **self.kwargs_object))


def save_project(field, file_name="file.gc"):
    file_p = SAVES_PATH + f'{file_name}'
    try:
        print(f"'{file_p}' - SAVING...")
        data = {"components": field.components.get_vars(), "components_of_types": field.components_of_types,
                "version": VERSION}
        with open("save_data.json", 'w') as f:
            f.write(str(data))
        t = pickle.dumps(data)
        with open(file_p, 'wb') as f:
            f.write(t)
        print(f"File '{file_p}' is SAVED!")
        field.console.print(f"File '{file_p}' is saved!")
    except Exception as exc:
        print("Error saving:", exc)
        field.console.print(f"Error saving file '{file_p}': {exc}")
        return False
    finally:
        return True


def open_project(field, file_name="file.gc"):
    file_p = SAVES_PATH + f'{file_name}'
    try:
        print(f"'{file_p}' - open...")
        with open(file_p, 'rb') as f:
            data = pickle.load(f)
        version = data.get("game_version")
        if version != VERSION:
            field.console.print(f"Software version conflict, app version is {VERSION}, file version {version}")
            return
        components = data.get("components")
        field.components.set_vars(components)
        field.components_of_types = data.get("components_of_types")
        print(f"File '{file_p}' is loaded")
        field.console.print(f"File '{file_p}' is loaded")
    except Exception as exc:
        print("Error opening:", exc)
        field.console.print(f"Error opening file '{file_p}': {exc}")
        return False
    finally:
        return file_p
