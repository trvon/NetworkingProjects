from multiprocessing import Pool

def f(x):
	print("router", x)

with Pool(8) as p:
	routers = [int(c) for c in range(8)]
	processes = p.map(f, routers)
	# Accessing individual processes
	print(processes[0])