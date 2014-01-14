#!/usr/bin/env python
#
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os

from gremlins import faults, metafaults, triggers, hostutils

bastion = os.getenv("GREMLINS_BASTION_HOST", hostutils.guess_remote_host())

if not bastion:
  raise Exception("GREMLINS_BASTION_HOST not set, and I couldn't guess your remote host.")

logging.info("Using %s as bastion host for network failures. You should be able to ssh from that host at all times." % bastion)

fail_node_long = faults.fail_network(bastion, 300, ["Accumulo-All"])
# XXX make sure this is greater than ZK heartbeats
fail_node_short = faults.fail_network(bastion, 45, ["Accumulo-All"])
# XXX make sure this is less than ZK heartbeats
fail_node_transient = faults.fail_network(bastion, 10, ["Accumulo-All"])

profile = [
  triggers.Periodic(
    60,
    metafaults.maybe_fault(
      0.14,
      metafaults.pick_fault([
        (1, fail_node_long),
        (1, fail_node_short),
        (2, fail_node_transient),
      ]))
    ),
  ]

