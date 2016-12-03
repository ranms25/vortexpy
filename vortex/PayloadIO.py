"""
 * Created by Synerty Pty Ltd
 *
 * This software is open source, the MIT license applies.
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
"""
import logging
import traceback
from datetime import datetime

from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

logger = logging.getLogger(name="PayloadIO")


class PayloadIO(object):
    '''
    PayloadIO, Processes payloads received from the vortex and distributes
    them to where they need to go.
    '''

    # Singleton
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(PayloadIO, cls).__new__(cls)
            cls._instance.__singleton_init__()
        return cls._instance

    def __singleton_init__(self):
        self._endpoints = set()

    def remove(self, endpoint):
        if endpoint in self._endpoints:
            self._endpoints.remove(endpoint)

    def add(self, endpoint):
        self._endpoints.add(endpoint)

    @property
    def endpoints(self):
        ''' Endpoints property

        @:return a copy of the list of endpoints
        '''
        return list(self._endpoints)

    def process(self, payload, **kwargs):
        immutableEndpoints = list(self._endpoints)
        for endpoint in immutableEndpoints:
            reactor.callLater(0, self._processLater, endpoint, payload, **kwargs)

    def _processLater(self, endpoint, payload, **kwargs):
        startDate = datetime.utcnow()

        def respondToException(exception):
            ''' Respond To Exception
            Putting the exception into a failure messes with the stack, hence the
            common function
            '''
            from Vortex import vortexSendPayload
            from Payload import Payload

            vortexSendPayload(Payload(filt=payload.filt,
                                      result=exception.message),
                              kwargs['vortexUuid'])
            logger.exception(exception)

        def errback(failure):
            respondToException(failure.value)

        def callback(value):
            secondsTaken = (datetime.utcnow() - startDate).total_seconds()
            if secondsTaken > 0.3:
                func = logger.warning if secondsTaken < 0.8 else logger.critical
                func("Payload endpoint for took %s\npayload.filt=%s\n%s" % (
                    secondsTaken,
                    payload.filt,
                    endpoint))

        try:
            d = endpoint.process(payload, **kwargs)
            if isinstance(d, Deferred):
                d.addCallback(callback)
                d.addErrback(errback)
            else:
                callback(True)

        except Exception as e:
            respondToException(e)