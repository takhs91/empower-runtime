#!/usr/bin/env python3
#
# Copyright (c) 2015, Roberto Riggio
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the CREATE-NET nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY CREATE-NET ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL CREATE-NET BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Bytes counters module."""

from empower.core.module import ModuleHandler
from empower.core.module import bind_module
from empower.core.restserver import RESTServer
from empower.charybdis.lvapp.lvappserver import LVAPPServer
from empower.charybdis.counters.counters import PT_STATS_RESPONSE
from empower.charybdis.counters.counters import STATS_RESPONSE
from empower.charybdis.counters.counters import CounterWorker
from empower.charybdis.counters.counters import Counter

from empower.main import RUNTIME

import empower.logger
LOG = empower.logger.get_logger()


class BytesCounter(Counter):

    """ Stats returning byte counters """

    def fill_samples(self, data):
        """ Compute samples. """

        samples = sorted(data, key=lambda entry: entry[0])

        out = [0] * len(self.bins)

        for entry in samples:
            if len(entry) == 0:
                continue
            size = entry[0]
            count = entry[1]
            for i in range(0, len(self.bins)):
                if size <= self.bins[i]:
                    out[i] = out[i] + size * count
                    break

        return out


class BytesCounterHandler(ModuleHandler):
    pass


class BytesCounterWorker(CounterWorker):

    MODULE_NAME = "bytes_counter"
    MODULE_HANDLER = BytesCounterHandler
    MODULE_TYPE = BytesCounter


bind_module(BytesCounterWorker)


def launch():
    """ Initialize the module. """

    lvap_server = RUNTIME.components[LVAPPServer.__module__]
    rest_server = RUNTIME.components[RESTServer.__module__]

    worker = BytesCounterWorker(rest_server)
    lvap_server.register_message(PT_STATS_RESPONSE,
                                 STATS_RESPONSE,
                                 worker.handle_stats_response)

    return worker