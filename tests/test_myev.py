import os
import sys
import unittest

import validators as v_validators

import myev
from myev import validators


class EnvironmentTestCase(unittest.TestCase):
    def test_environment(self):
        config = dict(
            BOOLEAN_A=(bool, None),
            BOOLEAN_B=(bool, []),
            BOOLEAN_C=(bool,),
            BOOLEAN_D=bool,
            BOOLEAN_E=(bool, [validators.is_true]),
            BOOLEAN_F=(bool, [validators.is_false]),
            INT_A=(int, None),
            INT_B=(int, []),
            INT_C=(int,),
            INT_D=int,
            INT_E=(int, [validators.IsGreaterThan(0)]),
            INT_F=(int, [validators.IsLesserThan(0)]),
            INT_G=(int, [validators.IsEqualTo(0)]),
            STRING_A=(str, None),
            STRING_B=(str, []),
            STRING_C=(str,),
            STRING_D=str,
            STRING_E=(),
            STRING_F=None,
            STRING_G=(str, [v_validators.email]),
            STRING_H=(str, [v_validators.domain]),
            STRING_I=(str, [v_validators.url]),
        )
        values = dict(
            BOOLEAN_A='1',
            BOOLEAN_B='1',
            BOOLEAN_C='1',
            BOOLEAN_D='1',
            BOOLEAN_E='1',
            BOOLEAN_F='0',
            INT_A='1',
            INT_B='1',
            INT_C='1',
            INT_D='1',
            INT_E='1',
            INT_F='-1',
            INT_G='0',
            STRING_A='string',
            STRING_B='string',
            STRING_C='string',
            STRING_D='string',
            STRING_E='string',
            STRING_F='string',
            STRING_G='luke@localhost',
            STRING_H='localhost',
            STRING_I='https://localhost',
        )
        cast_values = dict(
            BOOLEAN_A=True,
            BOOLEAN_B=True,
            BOOLEAN_C=True,
            BOOLEAN_D=True,
            BOOLEAN_E=True,
            BOOLEAN_F=False,
            INT_A=1,
            INT_B=1,
            INT_C=1,
            INT_D=1,
            INT_E=1,
            INT_F=-1,
            INT_G=0,
            STRING_A='string',
            STRING_B='string',
            STRING_C='string',
            STRING_D='string',
            STRING_E='string',
            STRING_F='string',
            STRING_G='luke@localhost',
            STRING_H='localhost',
            STRING_I='https://localhost',
        )

        for key, value in values.items():
            os.environ[key] = value

        myev.Environment(**config).inject()
        module = sys.modules[__name__]

        for name in config.keys():
            self.assertTrue(hasattr(module, name))
            self.assertEqual(getattr(module, name), cast_values[name])
