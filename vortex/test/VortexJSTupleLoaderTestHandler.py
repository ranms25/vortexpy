import logging
from typing import List

from vortex.PayloadFilterKeys import plDeleteKey
from vortex.handler.ModelHandler import ModelHandler


from vortex.test.TestTuple import TestTuple

logger = logging.getLogger(__name__)

# If there were reallying going to a DB, we'd use OrmCrudHandler
class VortexJSTupleLoaderTestHandler(ModelHandler):
    def buildModel(self, payload, **kwargs):
        logger.debug("Received payload with %s tuples and filt=%s",
                     len(payload.tuples), payload.filt)

        data = []

        if payload.tuples:
            # Return nothing if this was a delete
            if plDeleteKey in payload.filt:
                # Return nothing, it was deleted
                pass

            else:
                # Else this was a save, just update some data and return id
                data = payload.tuples
                for testTuple in data:
                    testTuple.aInt += 10
                    testTuple.aBoolTrue = not testTuple.aBoolTrue

        else:
            # Else this is to get new data.

            for num in range(5):
                uniStr = "#%s double hyphen :-( — “fancy quotes”" % num
                data.append(TestTuple(aInt=num,
                                      aBoolTrue=bool(num % 2),
                                      aString= "This is tuple #%s" % num,
                                      aStrWithUnicode=uniStr))

        return data

__handler = VortexJSTupleLoaderTestHandler({
                    "key": "vortex.tuple-loader.test.data"
                })