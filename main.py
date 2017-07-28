from Model import Model
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