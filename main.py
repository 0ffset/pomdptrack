from Model import Model
import cPickle
import MDP
import POMDP
import time

if __name__ == "__main__":
	#grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	#		[0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
	#		[0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
	#		[0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
	#		[0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
	#		[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
	
	grid = [[0, 0, 0, 0, 0, 0, 0, 0],
			[0, 0, 1, 0, 0, 1, 0, 0],
			[1, 1, 1, 0, 0, 1, 1, 1],
			[0, 0, 1, 0, 0, 1, 0, 0],
			[0, 0, 0, 0, 0, 0, 0, 0]]
	numAgents = 1
	numTargets = 2

	model = Model(grid, numAgents, numTargets)
	print "Initial state:"
	model.printWorld()
	print "\n==============================================================================\n"
	timeStep = 0.75
	while True:
		raw_input("Press ENTER for next time step.\n")
		start = time.time()
		model.update(True)
		elapsedTime = time.time() - start
		#time.sleep(max(0, timeStep - elapsedTime))






























"""
if __name__ == "__main__":
	# Specify grid world. 1 = wall, 0 = no wall
	grid = [[0, 0, 0, 0, 0],
			[0, 0, 1, 0, 0],
			[0, 0, 1, 0, 0],
			[0, 0, 1, 0, 0],
			[0, 0, 0, 0, 0]]

	# Set initial state
	agentInitCompoundState = ((0, 0),) # initial states for all agents
	targetInitCompoundState = ((4, 4),) # initial states for all targets
	initState = (agentInitCompoundState, targetInitCompoundState) # initial system state
	numAgents = len(agentInitCompoundState)
	numTargets = len(targetInitCompoundState)

	# Generate POMDP model
	model1 = Model(grid, numAgents, numTargets, initState)

	S = len(model1.states)
	A = len(model1.actions)
	O = len(model1.observations)
	discount = 0.95
	horizon = 2
	maxReward = -0.5
	
	transitionFcn = model1.transitionFcn.getTAsMatrix()
	observationFcn = model1.observationFcn.getOAsMatrix()
	rewardFcn = [[[-0.5 for k in range(S)] for j in range(A)] for i in range(S)]

	model = POMDP.Model(O, S, A)

	model.setTransitionFunction(transitionFcn)
	model.setObservationFunction(observationFcn)
	model.setRewardFunction(rewardFcn)

	model.setDiscount(discount)

	policy = POMDP.RTBSSModel(model, maxReward)

	totalReward = 0.0

	b = [0.0 for i in range(S)]
	s = model1.states.index(initState)#random.randrange(0, S)
	for targetCompoundState in model1.targetCompoundStates:
		b[model1.states.index((agentInitCompoundState, targetCompoundState))] = 1.0/len(model1.targetCompoundStates)

	model1.printWorld()

	while True:
		a, v = policy.sampleAction(b, horizon)

		#print("a: %s %s, v: %f" % (actionLabels[a], actions[a], v))

		#print("s: %i" % s)
		s, o, r = model.sampleSOR(s, a)

		#print("s': %i, o: %s, r: %f" % (s, observations[o], r))

		totalReward += r

		b = POMDP.updateBelief(model, b, a, o)
		b_list = [0.0]*MDP.Vector.__len__(b)
		for i in range(MDP.Vector.__len__(b)):
			b_list[i] = MDP.Vector.__getitem__(b, i)
		#print(b_list)
		bMax = max(b_list)
		print("max(b): %f" % bMax)
		agentMaxState, targetMaxState = set(), set()
		#for stateIndex in range(S):
		#	if b_list[stateIndex] == bMax:
		#		agentMaxState.add(states[stateIndex][0])
		#		targetMaxState.add(states[stateIndex][1])
		#print("agent max: %s, target max: %s" % (agentMaxState, targetMaxState))

		model1.state = model1.states[s]
		model1.printWorld()

		time.sleep(.25)


	#transitionFcn = model.transitionFcn.getTAsMatrix()
	#cPickle.dump(transitionFcn, open("transitionFcn.pkl", "wb"))
	#transitionFcnDict = model.transitionFcn.T
	#cPickle.dump(transitionFcnDict, open("transitionFcnDict.pkl", "wb"))
	#print "Loading T..."
	#transitionFcn = cPickle.load(open("transitionFcn.pkl", "rb"))
	#print "T loaded."

	#observationFcn = model.observationFcn.getOAsMatrix()
	#cPickle.dump(observationFcn, open("observationFcn.pkl", "wb"))
	#observationFcnDict = model.observationFcn.O
	#cPickle.dump(observationFcnDict, open("observationFcnDict.pkl", "wb"))
	#print "Loading O..."
	#observationFcn = cPickle.load(open("observationFcn.pkl", "rb"))
	#print "O loaded."

	print "Done."
"""