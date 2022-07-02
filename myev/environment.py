import inspect
import os
import sys


class Environment(dict):
    """
    Pass tuples or type to constructor:
    * tuple(cast type, validators)
    * tuple(cast type)
    * cast type
    """

    @staticmethod
    def get_calling_module(frame_info):
        return inspect.getmodule(frame_info.frame)

    @staticmethod
    def get_main_module():
        return sys.modules['__main__']

    @staticmethod
    def get_tuple_config(something):
        match len(something):
            case 0:
                return str, []
            case 1:
                return something[0], []
            case 2:
                validators = something[1]
                if validators is None:
                    validators = []
                return something[0], validators
            case _:
                raise ValueError('Invalid tuple size.')

    def get_cast_and_validators(self, something):
        if type(something) == type:
            return something, []
        elif type(something) == tuple:
            return self.get_tuple_config(something)
        elif something is None:
            return str, []
        else:
            raise ValueError('Invalid type.')

    @staticmethod
    def get_cast_value(cast, value):
        if cast is str:
            return value  # no cast
        elif cast is bool:
            return bool(int(value))  # '0' or '1'
        elif cast is int:
            return int(value)  # str to int
        else:
            raise ValueError('Invalid cast.')

    def set_attributes(self, module):
        for key, something in self.items():
            cast, validators = self.get_cast_and_validators(something)
            value = os.environ[key]
            cast_value = self.get_cast_value(cast, value)
            for validator in validators:
                validator(cast_value)
            setattr(module, key, cast_value)

    def inject(self):
        frame_info = inspect.stack()[1]
        module = self.get_calling_module(frame_info)
        if module is None:  # in __main__
            module = self.get_main_module()
        self.set_attributes(module)