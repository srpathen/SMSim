class SM:
    # This function will take in a state type, an association between a variable name and the type associated with the name
    def __init__(self, SMInputType: type=int, stateIDType: type=int, stateType: dict[str,type] = dict(), inputType: type=int, errorOnUnresInput: bool=True):
        self.stateType = stateType
        self.stateIDType = stateIDType
        self.inputType = inputType

        self.errorOnUnresInput = errorOnUnresInput
        
        self.stateTransitionTable = dict()
        self.reverseTransitionTable = dict()
        
        self.states = dict()
        self.endStates = []
        self.initialState = None
        self.state = None

    def enforceType(self, variableName, variable, correctType):
        if (type(variable) != correctType):
            raise TypeError(f"{variableName} is of type {type(variable)}. Expected type of {correctType}")

    def checkIfValidStateID(self, stateID, checkIfInStates=True):
        # First check the type of the state ID
        self.enforceType("state ID", stateID, self.stateIDType)
        # Next check if this state is in the states dictionary
        if not checkIfInStates:
            return
        if not stateID in self.states:
            raise KeyError(f"{stateID} was not added to the state machine")
    
    def checkIfStateValid(self, state:dict):
        for var in state:
            if not var in self.stateType:
                raise KeyError(f"Invalid variable name: {var}")
            self.enforceType(var, state[var], self.stateType[var])
        for var in self.stateType:
            if not var in state:
                raise Exception("{var} not found in the state") 

    def printState(self, stateID):
        self.checkIfValidStateID(stateID)
        for var in self.states[stateID]:
            print(f"|-->{var}={self.states[stateID][var]}")

    def printTransitions(self, stateID):
        self.checkIfValidStateID(stateID)
        for input in self.stateTransitionTable[stateID]:
            print(f"|-->Input={input}->State={self.stateTransitionTable[stateID][input]}")
        
    def print(self):
        # First print the states
        print("Printing the states in the State Machine")
        for stateID in self.states:
            print(f"State ID: {stateID}")
            self.printState(stateID)
        # Then print the state transition table
        print("\nPrinting the states transition table")
        for stateID in self.stateTransitionTable:
            print(f"State ID: {stateID}")
            self.printTransitions(stateID)
        print()
            
    def addState(self, stateID, state:dict):
        # When we add a state, we need to provide a state ID
        self.checkIfValidStateID(stateID, checkIfInStates=False)
        if stateID in self.states:
            raise LookupError("State ID has already been used")
        self.checkIfStateValid(state)
        self.states[stateID] = state

    def changeState(self, stateID, state:dict):        
        self.checkIfValidStateID(stateID)
        self.checkIfStateValid(state)
        self.states[stateID] = state

    def removeState(self, stateID):
        self.checkIfValidStateID(stateID)

        del self.states[stateID]

        if stateID in  self.stateTransitionTable:
            del self.stateTransitionTable[stateID]

        if stateID in self.reverseTransitionTable:
            # Go through all sources in the reverse transition table
            for pair in self.reverseTransitionTable[stateID]:
                # delete the source, input pairs that result in the destination ID
                del self.stateTransitionTable[pair[0]][pair[1]]
                if self.stateTransitionTable[pair[0]] == dict():
                    del self.stateTransitionTable[pair[0]]

            del self.reverseTransitionTable[stateID]

    def addStateTransition(self, sourceID, destinationID, input):
        self.checkIfValidStateID(sourceID)
        self.checkIfValidStateID(destinationID)
        self.enforceType("input",input,self.inputType)

        if not sourceID in self.stateTransitionTable:
            self.stateTransitionTable[sourceID] = dict()

        if not destinationID in self.reverseTransitionTable:
            self.reverseTransitionTable[destinationID] = []

        if input in self.stateTransitionTable[sourceID]:
            raise Exception(f"Input transition of {input} already set for state given by state ID: {sourceID}")
        
        self.stateTransitionTable[sourceID][input] = destinationID
        self.reverseTransitionTable[destinationID].append([sourceID, input])
        
    def removeStateTransition(self, sourceID, destinationID, input):
        self.checkIfValidStateID(sourceID)
        self.checkIfValidStateID(destinationID)
        self.enforceType("input",input,self.inputType)

        if not sourceID in self.stateTransitionTable:
            raise KeyError(f"Source ID not found in transition table: {sourceID}")
        if not sourceID in self.stateTransitionTable:
            raise KeyError(f"Destination ID not found in transition table: {destinationID}")
        
        if not input in self.stateTransitionTable[sourceID]:
            raise KeyError(f"{input} not found in transition table for {sourceID}")
        
        del self.stateTransitionTable[sourceID][input]
        self.reverseTransitionTable[destinationID].remove((sourceID, input))

    def setInitialState(self, stateID):
        self.checkIfValidStateID(stateID)
        self.initialState = stateID
    
    def input(self, input):
        self.enforceType("input",input,self.inputType)

        if self.state == None:
            if self.initialState == None:
                raise Exception("Initial state not set")
            self.state = self.initialState

        if not input in self.stateTransitionTable[self.state]:
            if self.errorOnUnresInput:
                raise Exception(f"Unresolved input {input} for state with ID {self.state}")
            else:
                return
        
        self.state = self.stateTransitionTable[self.state][input]

    def restart(self):
        if self.state == None:
            raise Exception("Initial state not set")
        self.state = self.initialState