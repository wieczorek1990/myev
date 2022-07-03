import abc

from validators import utils  # type: ignore


@utils.validator
def is_true(value):
    return value is True


@utils.validator
def is_false(value):
    return value is False


class Validator:
    @abc.abstractmethod
    def validate(self, value):
        pass

    @utils.validator
    def __call__(self, value, *args, **kwargs):
        return self.validate(value)


class ValueValidator(Validator, abc.ABC):
    def __init__(self, value):
        self.value = value


class IsGreaterThan(ValueValidator):
    def validate(self, value):
        return value > self.value


class IsLesserThan(ValueValidator):
    def validate(self, value):
        return value < self.value


class IsEqualTo(ValueValidator):
    def validate(self, value):
        return value == self.value
