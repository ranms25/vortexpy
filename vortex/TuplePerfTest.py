from datetime import datetime

import os
import psutil

process = psutil.Process(os.getpid())

ITER_COUNT = 1000 * 1000 * 5

RESULT = None


def makeL(i):
    # Use this line to negate the effect of the strings on the test
    # return "Python is smart and will only create one string with this line"

    # Use this if you want to see the difference with 5 million unique strings
    return "This is a sample string %s" % i


def timeit(method):
    def timed(*args, **kw):
        global RESULT
        s = datetime.now()
        RESULT = method(*args, **kw)
        e = datetime.now()

        sizeMb = process.memory_info().rss / 1024 / 1024
        sizeMbStr = "{0:,}".format(round(sizeMb, 2))

        print('Time Taken = %s, \t%s, \tSize = %s' % (e - s, method.__name__, sizeMbStr))

    return timed


from vortex.Tuple import Tuple, addTupleType, TupleHash
from vortex.Payload import Payload


@addTupleType
class X(Tuple):
    __tupleType__ = "X"
    __slots__ = ["i", "l"]



@timeit
def provile_dict_of_nt():
    return [X(i=i, l=makeL(i)) for i in range(ITER_COUNT)]


if __name__ == "__main__":
    provile_dict_of_nt()

    tupleIn = X("val1", "val2")
    vortexMsg = Payload(tuples=[tupleIn]).toVortexMsg()
    payload = Payload().fromVortexMsg(vortexMsg)

    assert TupleHash(tupleIn) == TupleHash(payload.tuples[0])
