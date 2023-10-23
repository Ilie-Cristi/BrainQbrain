import logging
from dataclasses import dataclass
import numpy as np

from netqasm.sdk import Qubit
from netqasm.sdk.classical_communication.message import StructuredMessage
from netqasm.sdk.toolbox.state_prep import set_qubit_state

from squidasm.run.stack.run import run
from squidasm.sim.stack.common import LogManager
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util import create_two_node_network, get_qubit_state, get_reference_state


class ClinicProgram(Program):
    PEER_NAME = "Hospital"

    def __init__(self, data_patients):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)
        self.data_patients = data_patients.flatten()

        #The number of teleported qubits will be the number of patients * the number of features,
        # each feature is expressed here as phi and theta
        self._num_teleported_qubits = self.data_patients.shape[0]//2


    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="controller_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=20,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        # Communicate with the hospital about the number of qubits transmitted
        csocket.send(self._num_teleported_qubits)

        original_probs = []
        for i in range(self._num_teleported_qubits):
            q = Qubit(connection)
            set_qubit_state(q, self.data_patients[2*i], self.data_patients[2*i+1])
            # Create EPR pairs
            epr = epr_socket.create_keep()[0]
            # Teleport
            q.cnot(epr)
            q.H()
            m1 = q.measure()
            m2 = epr.measure()
            yield from connection.flush()
            # Send the correction information
            m1, m2 = int(m1), int(m2)

            self.logger.info(
                f"Performed teleportation protocol with measured corrections: m1 = {m1}, m2 = {m2}"
            )

            csocket.send_structured(StructuredMessage("Corrections", f"{m1},{m2}"))

            original_dm = get_reference_state(self.data_patients[2*i], self.data_patients[2*i+1])

            original_probs.append(abs(original_dm[0][0]))
            original_probs.append(abs(original_dm[0][1]))

        return {"original_probs": original_probs}


class HospitalProgram(Program):
    PEER_NAME = "Clinic"

    def __init__(self):
        self.logger = LogManager.get_stack_logger(self.__class__.__name__)

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="controller_program",
            csockets=[self.PEER_NAME],
            epr_sockets=[self.PEER_NAME],
            max_qubits=20,
        )

    def run(self, context: ProgramContext):
        csocket = context.csockets[self.PEER_NAME]
        epr_socket = context.epr_sockets[self.PEER_NAME]
        connection = context.connection

        self._num_received_qubits = yield from csocket.recv()
        final_probs = []
        for _ in range(self._num_received_qubits):
            epr = epr_socket.recv_keep()[0]
            yield from connection.flush()
            self.logger.info("Created EPR pair")

            # Get the corrections
            msg = yield from csocket.recv_structured()
            print(msg)
            assert isinstance(msg, StructuredMessage)
            m1, m2 = msg.payload.split(",")
            self.logger.info(f"Received corrections: {m1}, {m2}")
            if int(m2) == 1:
                self.logger.info("performing X correction")
                epr.X()
            if int(m1) == 1:
                self.logger.info("performing Z correction")
                epr.Z()

            yield from connection.flush()

            final_dm = get_qubit_state(epr, "Hospital")

            final_probs.append(abs(final_dm[0][0]))
            final_probs.append(abs(final_dm[0][1]))

        return {"final_probs": final_probs}

