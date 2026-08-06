import logging
import cirq
from typing import Dict, Any, Union

try:
    from qiskit import QuantumCircuit
    from qiskit_aer import Aer
except ImportError:
    QuantumCircuit = None
    Aer = None

class QuantumExecution:
    """
    Executes quantum circuits on local simulators (Google Cirq or IBM Qiskit).
    """
    def __init__(self):
        self.cirq_simulator = cirq.Simulator()
        if Aer:
            from qiskit_aer import AerSimulator
            self.qiskit_simulator = AerSimulator()
        else:
            self.qiskit_simulator = None
        logging.info("QuantumExecution layer initialized.")

    def execute_circuit(self, circuit: Union[cirq.Circuit, 'QuantumCircuit'], repetitions: int = 1000) -> Dict[str, Any]:
        """
        Executes the provided circuit on the appropriate simulator and returns result histogram.
        """
        logging.info(f"Executing quantum circuit with {repetitions} repetitions...")
        
        # Check if circuit is Qiskit QuantumCircuit
        if QuantumCircuit and isinstance(circuit, QuantumCircuit):
            return self._execute_qiskit(circuit, repetitions)
        elif isinstance(circuit, cirq.Circuit):
            return self._execute_cirq(circuit, repetitions)
        else:
            return self._format_error("Unsupported circuit type or framework not installed.")

    def _execute_cirq(self, circuit: cirq.Circuit, repetitions: int) -> Dict[str, Any]:
        try:
            result = self.cirq_simulator.run(circuit, repetitions=repetitions)
            measurement_keys = list(result.measurements.keys())
            
            if not measurement_keys:
                raise ValueError("No measurement gates found in the circuit.")
            
            key = measurement_keys[0]
            counts = result.histogram(key=key)
            
            qubits = sorted(list(circuit.all_qubits()))
            qubit_count = len(qubits)
            
            histogram_bitstrings = {}
            for int_state, count in counts.items():
                binary_str = format(int_state, f'0{qubit_count}b')
                histogram_bitstrings[binary_str] = int(count)

            return self._format_success(histogram_bitstrings, counts, repetitions)
            
        except Exception as e:
            logging.error(f"Cirq quantum execution failed: {e}")
            return self._format_error(str(e))

    def _execute_qiskit(self, circuit: 'QuantumCircuit', repetitions: int) -> Dict[str, Any]:
        if not self.qiskit_simulator:
            return self._format_error("Qiskit simulator (Aer) not available.")
            
        try:
            # Qiskit V2 execute is typically done via backend.run(transpile(...))
            from qiskit import transpile
            transpiled_circuit = transpile(circuit, self.qiskit_simulator)
            job = self.qiskit_simulator.run(transpiled_circuit, shots=repetitions)
            result = job.result()
            counts = result.get_counts(transpiled_circuit)
            
            # Qiskit already returns bitstrings, but sometimes without leading zeros padding if missing
            qubit_count = circuit.num_qubits
            
            histogram_bitstrings = {}
            raw_counts = {}
            for bitstring, count in counts.items():
                # Remove spaces from Qiskit bitstring if any (from multiple classical registers)
                clean_bitstring = bitstring.replace(' ', '')
                # Ensure padding
                clean_bitstring = clean_bitstring.zfill(qubit_count)
                histogram_bitstrings[clean_bitstring] = count
                # convert bitstring back to int for raw_counts consistency with cirq logic
                int_state = int(clean_bitstring, 2)
                raw_counts[str(int_state)] = count

            return self._format_success(histogram_bitstrings, raw_counts, repetitions)
            
        except Exception as e:
            logging.error(f"Qiskit quantum execution failed: {e}")
            return self._format_error(str(e))

    def _format_success(self, histogram_bitstrings: Dict[str, int], raw_counts: Dict[str, int], repetitions: int) -> Dict[str, Any]:
        if not histogram_bitstrings:
             return self._format_error("No measurements returned.")
             
        dominant_state = max(histogram_bitstrings, key=histogram_bitstrings.get)
        dominant_probability = float(histogram_bitstrings[dominant_state] / repetitions)
        
        execution_summary = {
            "success": True,
            "repetitions": repetitions,
            "raw_counts": {str(k): int(v) for k, v in raw_counts.items()},
            "bitstring_counts": histogram_bitstrings,
            "dominant_state": dominant_state,
            "dominant_probability": dominant_probability
        }
        logging.info(f"Quantum execution complete. Dominant state: {dominant_state} "
                     f"({dominant_probability:.1%})")
        return execution_summary
        
    def _format_error(self, error_msg: str) -> Dict[str, Any]:
        return {
            "success": False,
            "error": error_msg,
            "bitstring_counts": {},
            "dominant_state": "00",
            "dominant_probability": 0.0
        }
