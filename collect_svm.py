#!/usr/bin/env python2

import os, sys, math, time, subprocess, multiprocessing
from subprocess import check_call

dryrun = False

dataset = ["covtype", "webspam", "music", "rcv1", "epsilon", "news20"]
# settings used for grid size search
'''
nthreads = [10]
maxstepsize = {	"covtype" : 5e-2,
		"webspam" : 5e+0,
		"music"   : 5e-8,
		"rcv1"    : 1e-0,
		"epsilon" : 1e-1,
		"news20"  : 1e-0,
	   }
iterations = {	"default" : 200, "news20"  : 350, "epsilon" : 150}
stepdecay = [1, 0.95, 0.9, 0.85, 0.8]
stepdecay_per_dataset = {}
step_search_range = 10
'''
# settings used for collecting results
cpu_count = multiprocessing.cpu_count() / 2
if cpu_count <= 0:
	cpu_count = 1
# nthreads = [1, 2, 4, 8, 10, 15, 20, 30, 40]
nthreads = [cpu_count]
maxstepsize = { "covtype" : 5e-03,
		"webspam" : 2e-01,
		"music"   : 5e-08,
		"rcv1"    : 5e-01,
		"epsilon" : 1e-01,
		"news20"  : 5e-01,
	      }
stepdecay = []
stepdecay_per_dataset = { "covtype" : [0.85],
			  "webspam" : [0.8],
			  "music"   : [0.8],
			  "rcv1"    : [0.8],
			  "epsilon" : [0.85],
			  "news20"  : [0.8],
			}
iterations = {	"default" : 150, "epsilon" : 75}
step_search_range = 0

outputdir = "svm_" + time.strftime("%m%d-%H%M%S")

if len(sys.argv) > 1:
	if sys.argv[1] == "-n":
		dryrun = True
	if sys.argv[1] == "-y":
		dryrun = False

if not dryrun:
	check_call("mkdir -p {}/".format(outputdir), shell=True)

def GenerateSteps(max_step_size):
	steps = []
	step_size = max_step_size
	steps.append(format(step_size, '1.0e'))
	for i in range(0,step_search_range):
		first_digit = int(format(step_size, 'e')[0]);
		exp = math.floor(math.log10(step_size));
		if first_digit == 1:
			first_digit = 10
			exp -= 1
		first_digit /= 2
		step_size = first_digit * math.pow(10, exp)
		steps.append(format(step_size, '1.0e'))
	return steps

for d in dataset:
	# Find a step size from table
	steps = GenerateSteps(maxstepsize[d])
	if d in iterations:
		epochs = iterations[d]
	else:
		epochs = iterations["default"]
	print "For dataset {} we will use {} epochs and step size:\n {}\n".format(d, epochs, steps)
	for s in steps:
		for n in nthreads:
			if d in stepdecay_per_dataset:
				stepdecay_trials = stepdecay_per_dataset[d]
			else:
				stepdecay_trials = stepdecay
			for b in stepdecay_trials:
				cmdline = "bin/svm --epoch {} --binary 1 --stepinitial {} --step_decay {} --split {} data/{}_train.bin data/{}_test.bin".format(epochs, s, b, n, d, d)
				result_name = os.path.join(outputdir, "{}_{}_{}_{}.txt".format(d, n, s, b))
				print "Executing HogWild! with {} threads:\n{}\nResults at {}".format(n, cmdline, result_name)
				if not dryrun:
						result = subprocess.Popen(cmdline, shell=True, stdout=subprocess.PIPE).stdout.read()
						with open(result_name, "w") as f:
							f.write(result)
				else:
					print "*** This is a dry run. No results will be produced. ***"
	print


