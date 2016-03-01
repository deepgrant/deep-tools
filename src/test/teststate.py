#!/usr/bin/env python
import os
import sys
import pdb
import unittest

sys.path.insert(0, os.path.abspath('../deep/tools'))
sys.path.insert(0, os.path.abspath('./'))

import state

class EV_one(state.event): pass
class EV_two(state.event): pass
class EV_three(state.event): pass
class EV_four(state.event): pass

class ST_A(state.state):
    def __init__(self):
        state.state.__init__(self)

    def transitions(self):
        self.trans = {
            EV_one()   : ST_B(),
            EV_two()   : ST_C(),
            EV_three() : ST_D(),
        }

class ST_B(state.state):
    def __init__(self):
        state.state.__init__(self)

    def transitions(self):
        self.trans = {
            EV_one()   : ST_B(),
            EV_two()   : ST_C(),
        }

class ST_C(state.state):
    def __init__(self):
        state.state.__init__(self)

    def transitions(self):
        self.trans = {
            EV_two()   : ST_A(),
        }

class ST_D(state.state):
    def __init__(self):
        state.state.__init__(self)

    def transitions(self):
        self.trans = {
            EV_four()  : ST_E(),
        }

    def run(self, event):
        return EV_four()

class ST_E(state.state):
    def __init__(self):
        state.state.__init__(self)

    def transitions(self):
        self.trans = {
        }

class TestFSM1(unittest.TestCase):

    def setUp(self) :
        self.fsm = state.machine(ST_A())

    def testEvent1(self):
        self.fsm.injectEvent(EV_one())
        self.fsm.injectEvent(EV_one())
        self.fsm.injectEvent(EV_two())
        self.fsm.injectEvent(EV_two())

        self.assertTrue('.ST_A' in str(self.fsm.currentState))

    def testEvent2(self):
        self.fsm.injectEvent(EV_two())
        self.fsm.injectEvent(EV_two())

        self.assertTrue('.ST_A' in str(self.fsm.currentState))

    def testTrans(self):
        self.fsm.injectEvent(EV_three())

        self.assertTrue('.ST_E' in str(self.fsm.currentState))

def testSuite():
    _tests = ['testEvent1',
              'testEvent2',
              'testTrans',]

    _suite = unittest.TestSuite(map(TestFSM1, _tests))

    return _suite


if __name__ == '__main__':
    _testRunner = unittest.TextTestRunner(verbosity=2)

    _suites     = [testSuite(),]

    _allTests   = unittest.TestSuite(_suites)
    _testRunner.run(_allTests)

