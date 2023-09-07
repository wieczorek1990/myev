import inspect
import os
import sys

from myev import validators


class Environment(dict):
    """
    Pass tuples or cast callable to constructor as keyword argument in following
    format:
    * tuple(cast callable, validators list)
    * tuple(cast callable, validator)
    * tuple(cast callable, [])
    * tuple(cast callable)
    * cast callable
    """

    def __init__(self, defaults=None, **kwargs):
        self.defaults = defaults
        super().__init__(**kwargs)
        self.set_cast_values()

    def get_default(self, key):
        if self.defaults is None:
            return None
        return self.defaults.get(key)

    def set_cast_values(self):
        for key, something in self.items():
            cast, all_validators = self.get_cast_and_validators(something)
            default = self.get_default(key)
            value = os.environ.get(key, default)
            cast_value = self.get_cast_value(cast, value)
            for validator in all_validators:
                maybe_error = validator(cast_value)
                if isinstance(maybe_error, validators.ValidationError):
                    raise maybe_error
            self[key] = cast_value

    @staticmethod
    def get_tuple_config(something):
        size = len(something)
        match size:
            case 1:
                cast = something[0]
                return cast, []
            case 2:
                cast, maybe_validators = something
                if callable(maybe_validators):
                    maybe_validators = [maybe_validators]
                return cast, maybe_validators
            case _:
                raise ValueError(f"Invalid tuple size: {size}.")

    def get_cast_and_validators(self, something):
        something_type = type(something)
        if something_type == tuple:
            return self.get_tuple_config(something)
        if something_type == type:
            return something, []
        if callable(something):
            return something, []
        raise ValueError(f"Invalid type: {something_type}.")

    @staticmethod
    def get_cast_value(cast, value):
        if cast is bool:
            return bool(int(value))
        if callable(cast):
            return cast(value)
        raise ValueError(f"Invalid cast: {cast}.")

    @staticmethod
    def get_calling_module(frame_info):
        return inspect.getmodule(frame_info.frame)

    @staticmethod
    def get_main_module():
        return sys.modules["__main__"]

    def set_attributes(self, module):
        for key, value in self.items():
            setattr(module, key, value)

    def inject(self):
        """
        Injects keyword arguments passed to Environment
        into calling module.
        """
        frame_info = inspect.stack()[1]
        module = self.get_calling_module(frame_info)
        if module is None:  # in __main__
            module = self.get_main_module()
        self.set_attributes(module)

    def rename(self, old_key, new_key):
        self[new_key] = self.pop(old_key)
