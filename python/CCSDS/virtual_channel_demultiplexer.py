#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 Athanasios Theocharis <athatheoc@gmail.com>
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
from gnuradio import gr
from . import telemetry
import pmt

class virtual_channel_demultiplexer(gr.basic_block):
    """
    docstring for block virtual_channel_demultiplexer
    """
    def __init__(self, vc_outputs):
        gr.basic_block.__init__(self,
            name="virtual_channel_demultiplexer",
            in_sig=[],
            out_sig=[])

        self.vc_outputs = vc_outputs
        self.message_port_register_in(pmt.intern('in'))

        self.outputDict = {}
        for i in range(len(vc_outputs)):
            self.outputDict[vc_outputs[i]] = i
            self.message_port_register_out(pmt.intern('out' + str(i)))

        self.message_port_register_out(pmt.intern('discarded'))
        self.set_msg_handler(pmt.intern('in'), self.handle_msg)

    def handle_msg(self, msg_pmt):
        msg = pmt.cdr(msg_pmt)
        if not pmt.is_u8vector(msg):
            print("[ERROR] Received invalid message type. Expected u8vector")
            return
        packet = bytearray(pmt.u8vector_elements(msg))

        try:
            data = telemetry.PrimaryHeader.parse(packet[:])
        except:
            print("Could not decode telemetry primary header")
            return

        outPort = data.virtual_channel_id
        try:
            port = self.outputDict[outPort]
        except KeyError:
            self.message_port_pub(pmt.intern('discarded'), msg_pmt)
            print("Discarded message")
        else:
            self.message_port_pub(pmt.intern('out' + str(port)), msg_pmt)
