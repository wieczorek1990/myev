import inspect
import os
import sys


class Environment(dict):
    """
    Pass tuples or cast callable to constructor as keyword argument in following
    format:
    * tuple(cast callable, validators list)
    * tuple(cast callable, validator)
    * tuple(cast callable, [])
    * tuple(cast callable, None)
    * tuple(cast callable)
    * tuple()
    * cast callable
    * None
    """

    def __init__(self, defaults=None, **kwargs):
        self.defaults = defaults
        super().__init__(**kwargs)
        self.set_cast_values()

    def set_cast_values(self):
        for key, something in self.items():
            cast, validators = self.get_cast_and_validators(something)
            if self.defaults is not None:
                default = self.defaults.get(key)
            else:
                default = None
            value = os.environ.get(key, default)
            cast_value = self.get_cast_value(cast, value)
            for validator in validators:
                validator(cast_value)
            self[key] = cast_value

    @staticmethod
    def get_calling_module(frame_info):
        return inspect.getmodule(frame_info.frame)

    @staticmethod
    def get_main_module():
        return sys.modules['__main__']

    @staticmethod
    def get_tuple_config(something):
        size = len(something)
        match size:
            case 0:
                return str, []
            case 1:
                return something[0], []
            case 2:
                validators = something[1]
                if validators is None:
                    validators = []
                elif callable(validators):
                    validators = [validators]
                return something[0], validators
            case _:
                raise ValueError(f'Invalid tuple size: {size}.')

    def get_cast_and_validators(self, something):
        something_type = type(something)
        if something_type == type:
            return something, []
        elif something_type == tuple:
            return self.get_tuple_config(something)
        elif something is None:
            return str, []
        elif inspect.isfunction(something):
            return something, []
        else:
            raise ValueError(f'Invalid type: {something_type}.')

    @staticmethod
    def get_cast_value(cast, value):
        if cast is str:
            return value
        elif cast is bool:
            return bool(int(value))
        elif cast is int:
            return int(value)
        elif inspect.isfunction(cast):
            return cast(value)
        else:
            raise ValueError(f'Invalid cast: {cast}.')

    def set_attributes(self, module):
        for key, value in self.items():
            setattr(module, key, value)

    def inject(self):
        """
        Injects keyword arguments passed to Environment into calling module.
        """
        frame_info = inspect.stack()[1]
        module = self.get_calling_module(frame_info)
        if module is None:  # in __main__
            module = self.get_main_module()
        self.set_attributes(module)

    def rename(self, old_key, new_key):
        self[new_key] = self.pop(old_key)
