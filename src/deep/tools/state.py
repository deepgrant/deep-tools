#!/usr/bin/env python

################################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Deep Grant
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import exception

import string
import datetime


class issue(exception.issue):
    def __init__(self, errorStr):
        exception.issue.__init__(self, errorStr)

_stateIdToName = {}
_eventIdToName = {}

def stateIdToName(hashId):
    if _stateIdToName.has_key(hashId) == False:
        raise issue((1, 'No such hashId.', hashId,))

    return _stateIdToName[hashId]

def eventIdToName(hashId):
    if _eventIdToName.has_key(hashId) == False:
        raise issue((1, 'No such hashId.', hashId,))

    return _eventIdToName[hashId]

class event(object):

    def __init__(self):
        _eventIdToName[self.__hash__()] = self.__repr__()

    def __repr__(self):
        return self.__class__.__module__ + '.' + self.__class__.__name__

    def __str__(self):
        return self.__repr__()

    def __cmp__(self, other):
        return cmp(self.__str__(), other.__str__())

    def __hash__(self):
        _retVal = hash(self.__repr__())
        return _retVal

class state(object):
    """
    Base class to define state.
    """
    def __init__(self):
        self.trans   = {}
        self.context = None

        _stateIdToName[self.__hash__()] = self.__repr__()

    def __repr__(self):
        return self.__class__.__module__ + '.' + self.__class__.__name__

    def __str__(self):
        return self.__repr__()

    def __cmp__(self, other):
        return cmp(self.__str__(), other.__str__())

    def __hash__(self):
        _retVal = hash(self.__repr__())
        return _retVal

    def onEntry(self):
        pass

    def onExit(self):
        pass

    def run(self, event):
        return None

    def next(self, event):
        if self.trans.has_key(event) == False:
            return None

        return self.trans[event]

    def transitions(self):
        pass

    def setContext(self, context):
        self.context = context

    def getContext(self):
        return self.context

class machine(object):
    """
    List of inputs can drive the state transitions.
    """
    def __init__(self, startState):
        """
        Construct the Machine.
        """
        self.currentState  = startState
        self.previousState = None
        self.history       = []

    def __timestamp(self):
        return str(datetime.datetime.now())

    def __markTransition(self, fromS, event, toS):
        return (self.__timestamp(),
                fromS,
                event,
                toS,)

    def __repr__(self):
        _lines = []
        _lines.append(self.__class__.__module__ + '.' + self.__class__.__name__)
        for _trans in self.history:
            _line = '[%s] (%s)-EV(%s)--> %s' % _trans
            _lines.append(_line)

        _line = 'Current State: %s' % (self.currentState,)
        _lines.append(_line)

        return string.join(_lines, '\n')

    def getContext(self):
        return None

    def __processTransitionsContext(self, state):
        if state.trans != {}:
            return

        state.setContext(self.getContext())
        state.transitions()
        for _trans in state.trans:
            state.trans[_trans].setContext(self.getContext())

    def injectEvent(self, event):
        """
        Inject the specified event into the Machines current state.
        """
        _events = [event]

        for _event in _events:
            self.__processTransitionsContext(self.currentState)

            _nextState = self.currentState.next(_event)
            if _nextState != None:

                # We have a next state based on current state and the
                # supplied event.

                # Since we are exiting the current state, execute
                # its onExit method.
                self.currentState.onExit()

                # Record the event and time.
                self.history.append(
                    self.__markTransition(self.currentState.__repr__(),
                                          _event.__repr__(),
                                          _nextState.__repr__()
                                          )
                    )

                self.previousState = self.currentState
                self.currentState  = _nextState

                # Execure the onEntry for the new state.
                self.currentState.onEntry()

                # Now we can ececute the run method for this state.
                _transitiveEvent = self.currentState.run(_event)

                if _transitiveEvent != None:
                    # The run method can return a EVENT to inject into the FSM.
                    # Ergo this is a transitive event that may cause a
                    # FSM transition. Add this to the events list.
                    _events.append(_transitiveEvent)

        # Return the current state after all the events have been processed.
        return self.currentState

################################################################################

if __name__ == "__main__":
    pass

