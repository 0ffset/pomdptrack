from World import World
from TransitionFunction import TransitionFunction
from ObservationFunction import ObservationFunction
import Util
import time
import numpy.random

class Model:
	def __init__(self, grid = None, numAgents = None, numTargets = None, initState = None, checkpoints = None, maxSteps = None):
		self.world = World(grid)
		self.numAgents = 1 if numAgents == None else numAgents
		self.numTargets = 1 if numTargets == None else numTargets
		self.state = self.__getDefaultInitState() if initState == None else initState
		self.checkpoints = self.__getDefaultCheckpoints() if checkpoints == None else checkpoints
		self.checkpointIndex = [0 for i in range(self.numAgents)]
		self.DEFAULT_MAX_STEPS = [20 for i in range(self.numAgents)]
		self.maxSteps = self.__getDefaultMaxSteps() if maxSteps == None else maxSteps

		# Initialize sets of all actions
		self.agentActionLabels = ["stay", "go N", "go E", "go S", "go W"]
		self.agentActions      = [(0, 0), (-1, 0), (0, 1), (1, 0), (0, -1)]
		#self.targetActionLabels = ["stay", "go N", "go NE", "go E", "go SE", "go S", "go SW", "go W", "go NW"]
		#self.targetActions      = [(0, 0), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
		self.targetActionLabels = ["stay", "go N", "go E", "go S", "go W"]
		self.targetActions      = [(0, 0), (-1, 0), (0, 1), (1, 0), (0, -1)]
		self.actions = Util.getOrderedCombinations(self.agentActions, self.numAgents)
		self.targetCompoundActions = Util.getOrderedCombinations(self.targetActions, self.numTargets)
		
		# Initialize lists of all states
		self.robotStates = []
		self.agentCompoundStates = []
		self.targetCompoundStates = []
		self.states = []
		self.__initStates()

		# Pre-calculate minimum no. of actions required to reach target robot state from each state
		self.minSteps = dict()
		self.__initMinSteps()

		# Initialize transition, observation and reward functions
		self.transitionFcn = TransitionFunction(self)
		self.observationFcn = ObservationFunction(self)
		self.observations = self.observationFcn.getObservations()
		self.rewardFcn = self.observationFcn.getRewardFunction() # Reward function is generated upon observation function init

		# Initialize belief
		self.belief = dict()
		self.__initBelief()

	def __getDefaultInitState(self):
		"""Generates and returns a default initial system state."""
		agentCompoundState = tuple((i, 0) for i in range(self.numAgents))
		targetCompoundState = tuple((i, self.world.gridNumCols-1) for i in range(self.numTargets))
		return (agentCompoundState, targetCompoundState)

	def __getDefaultCheckpoints(self):
		"""Generates and returns a default list of checkpoints"""
		checkpoints = [[] for i in range(self.numAgents)]
		for i in range(self.numAgents):
			state1 = (self.world.gridNumRows - 1, self.world.gridNumCols - 1)
			state2 = (0, 0)
			checkpoints[i] = [state1, state2]
		return checkpoints

	def __getDefaultMaxSteps(self):
		"""Returns default max steps between checkpoints."""
		maxSteps = [None for i in range(self.numAgents)]
		for i in range(self.numAgents):
			maxSteps[i] = self.DEFAULT_MAX_STEPS[i]
		return maxSteps

	def __initStates(self):
		"""Initializes all states system and sub-system states."""
		start = time.time()
		print "Initializing state space..."

		# Enumerate robot states
		for i in range(self.world.gridNumRows):
			for j in range(self.world.gridNumCols):
				state = (i, j)
				if self.world.isValidRobotState(state):
					self.robotStates.append(state)

		# Enumerate agent and target compound states
		self.agentCompoundStates = Util.getOrderedCombinations(self.robotStates, self.numAgents)
		self.targetCompoundStates = Util.getOrderedCombinations(self.robotStates, self.numTargets)

		# Enumerate system states
		for agentCompoundState in self.agentCompoundStates:
			for targetCompoundState in self.targetCompoundStates:
				self.states.append((agentCompoundState, targetCompoundState))

		stop = time.time()
		print "State space (" + str(len(self.states)) + " states) initialized successfully in " + str(stop - start) + " s."

	def __initMinSteps(self):
		"""Initializes the minimum steps function."""
		timeStart = time.time()
		for start in self.robotStates:
			for end in self.robotStates:
				self.minSteps[(start, end)] = self.getMinSteps(start, end)
		timeElapsed = time.time() - timeStart
		print "Calculated shortest paths in " + str(timeElapsed) + " s."

	def getMinSteps(self, start, end):
		"""Retrurns minimum steps required to get from start to end state in the grid."""
		if (start, end) in self.minSteps.keys():
			return self.minSteps[(start, end)]
		elif (end, start) in self.minSteps.keys():
			return self.minSteps[(end, start)] # shortest way there is also shortest way back reversed
		else:
			return self.__BFSMinSteps(start, end)

	def __BFSMinSteps(self, start, end):
		"""Returns minimum steps required to get from start to end using BFS."""
		visited = set()
		queue = [(start, 0)]
		while len(queue) > 0:
			node = queue.pop(0)
			state = node[0]
			numSteps = node[1]
			if state == end:
				return numSteps
			if state not in visited:
				visited.add(state)
				self.minSteps[(start, state)] = numSteps
				self.minSteps[(state, start)] = numSteps
				for action in self.agentActions:
					nextState = self.__getRobotEndState(state, action)
					queue.append((nextState, numSteps + 1))

	def __getRobotEndState(self, state, action):
		"""Return robot end state after taking action in initial state."""
		endState = (state[0] + action[0], state[1] + action[1])
		return endState if self.world.isValidRobotState(endState) else state


	def __initBelief(self):
		"""Initialize belief state."""
		for targetCompoundState in self.targetCompoundStates:
			self.belief[targetCompoundState] = 1.0/len(self.targetCompoundStates)

	def T(self, s1, a, s2):
		"""
		Evaluates transition function for given initial state, action and end state,
		i.e. returns probability of system ending up in s2 after starting in s1 and taking action a
		"""
		return self.transitionFcn.eval(s1, a, s2)

	def O(self, s, o):
		"""
		Evaluates observation function for given state and observation,
		i.e. returns probability of system making observation o in state s
		"""
		return self.observationFcn.eval(s, o)

	def R(self, s):
		"""Returns the reward associated with a system state."""
		penalty = -0.5
		if self.rewardFcn.get(s, None) != None:
			return self.rewardFcn[s]
		return penalty

	def getOptimalAction(self):
		"""Returns optimal action for current state."""

		# Determine actions allowed to take in order to get to next checkpoint in time
		action = tuple()
		for i in range(self.numAgents):
			self.maxSteps[i] -= 1
			allowedAgentActions = []
			agentState = self.state[0][i]
			checkpointIndex = self.checkpointIndex[i]
			end = self.checkpoints[i][checkpointIndex]
			for agentAction in self.agentActions:
				start = self.__getRobotEndState(agentState, agentAction)
				maximum = self.maxSteps[i]
				if self.getMinSteps(start, end) <= maximum:
					allowedAgentActions.append(agentAction)
			a = numpy.random.choice(len(allowedAgentActions))
			action += (allowedAgentActions[a],)
			if self.maxSteps[i] == 0:
				self.maxSteps[i] = self.DEFAULT_MAX_STEPS[i]
				self.checkpointIndex[i] = (self.checkpointIndex[i] + 1)%len(self.checkpoints[i])

		return action

	def update(self, doPrint = False):
		"""Updates system based on performed action."""
		printList = [] # List for simultaneous print later (to avoid twitchy print)

		# Calculate optimal action
		action = self.getOptimalAction()
		nextCheckpoints = [None for i in range(self.numAgents)]
		agentActionLabel = [None for i in range(self.numAgents)]
		for i in range(self.numAgents):
			nextCheckpoints[i] = self.checkpoints[i][self.checkpointIndex[i]]
			agentActionLabel[i] = self.agentActionLabels[self.agentActions.index(action[i])]
		printList.append("Action: " + str(agentActionLabel))
		printList.append("Next checkpoint: " + str(nextCheckpoints))
		printList.append("Max steps left: " + str(self.maxSteps))

		# Update system state
		agentCompoundState = self.state[0] 
		PT = self.transitionFcn.T[self.state][action]
		s = numpy.random.choice(range(len(PT)), p = PT.values())
		self.state = PT.keys()[s]
		printList.append("Reward: " + str(self.R(self.state)))

		# Make observation
		PO = self.observationFcn.O[self.state]
		o = numpy.random.choice(range(len(PO)), p = PO.values())
		observation = PO.keys()[o]
		printList.append("Made observation: " + str(observation))

		# Update belief
		agentCompoundEndState = self.state[0]
		start = time.time()
		self.belief = self.getNewBelief(self.belief, action, observation, agentCompoundState, agentCompoundEndState, printList)
		partialBelief = [dict() for i in range(self.numTargets)]
		for targetCompoundState in self.belief.keys():
			for i in range(self.numTargets):
				targetState = targetCompoundState[i]
				if partialBelief[i].get(targetState, None) == None:
					partialBelief[i][targetState] = 0
				partialBelief[i][targetState] += self.belief[targetCompoundState]
		stop = time.time()
		printList.append("Belief updated in " + str(stop - start) + " s.")
		printList.append("Max belief: " + str(max(self.belief.values())))
		printList.append("Number of states in belief: " + str(len(self.belief)))
		printList.append("Individual beliefs:")
		for i in range(self.numTargets):
			printList.append("\tTarget " + str(i+1) + ": " + str(len(partialBelief[i])))

		# Print results
		if doPrint:
			for i in range(self.numTargets):
				print "Belief target " + str(i+1) + " (sum: " + str(sum(partialBelief[i].values())) + "):"
				for targetState in partialBelief[i].keys():
					print str(targetState) + ": " + str(partialBelief[i][targetState])

			print "Belief: "
			for key in self.belief.keys():
				print str(key) + ": " + str(self.belief[key])
			self.printWorld()

		print "\n".join(printList)
		print "\n==============================================================================\n"

	def getNewBelief(self, belief, action, observation, agentCompoundState, agentCompoundEndState, printList = None):
		"""Get a new belief based on previous belief, action and observation."""
		newBelief = dict()
		
		# Calculate new unnormalized belief based on tau (belief transition function)
		possibleTargetCompoundEndStates = self.observationFcn.targetCompoundStatesFromObservation[observation][agentCompoundEndState]
		count = 0
		for targetCompoundEndState in possibleTargetCompoundEndStates:
			endState = (agentCompoundEndState, targetCompoundEndState)
			p = 0
			for targetCompoundState in belief.keys():
				state = (agentCompoundState, targetCompoundState)
				p += self.T(state, action, endState)*belief[targetCompoundState]
				count += 1
			newBelief[targetCompoundEndState] = self.O(endState, observation)*p
		
		# Normalize and remove entries with zero probability
		normFactor = sum(newBelief.values())
		for targetCompoundState in newBelief.keys():
			newBelief[targetCompoundState] /= normFactor
			if abs(newBelief[targetCompoundState]) < 0.00000000001: # Remove if probability is 0
				newBelief.pop(targetCompoundState)
		
		# Add info to print list, if applicable
		if printList != None:
			printList.append("Observation corresponds to " + str(len(possibleTargetCompoundEndStates)) + " possible target compound states.")
			printList.append("Iterations: " + str(count))

		return newBelief

	def printWorld(self):
		"""Print a 2D grid representation of current state in terminal."""
		self.world.printWorld(self.state)