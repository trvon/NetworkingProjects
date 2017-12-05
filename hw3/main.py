# Author:   Trevon and Gabon Williams
from multiprocessing import Pool
from router import Router
import string
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

# Router ID's
routerID = [str(i) for i in list(string.ascii_lowercase)[0:6]]

# Routing table with ports and router id's
table = { 'a' : 9000, 'b' : 9001, 'c' : 9002, 'd' : 9003, 'e' : 9004, 'f' : 9005 }

def router(x):
    router = Router(routerID[x], table[routerID[x]], files[x], table)
    router.run()

# Main calling code
p = Pool(processes=6)
try:
    routers = [ int(i) for i in range(6) ]
    processes = p.map(router, routers)
    p.join()

# Clean shutdown
except KeyboardInterrupt:
    print("\nClean exit")