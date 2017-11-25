from multiprocessing import Pool
from router import Router
import time

# Router functionality
files = [
    "files/a.dat",
    "files/b.dat",
    "files/c.dat",
    "files/d.dat",
    "files/e.dat",
    "files/f.dat"
]

port = [ 9000, 9001, 9002, 9003, 9004, 9005 ]


def router(x):
    router = Router(x, port[x], files[x])
    router.readFile()


# Main calling code
with Pool(8) as p:
    routers = [int(c) for c in range(6)]
    processes = p.map(router, routers)
    # Accessing individual processes
    # print(processes)
