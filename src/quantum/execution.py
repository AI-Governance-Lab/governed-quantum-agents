import logging
import cirq
from typing import Dict, Any

class QuantumExecution:
    """
    Executes Google Cirq quantum circuits on a local simulator.
    """
    def __init__(self):
        self.simulator = cirq.Simulator()
        logging.info("QuantumExecution layer initialized with cirq.Simulator.")

    def execute_circuit(self, circuit: cirq.Circuit, repetitions: int = 1000) -> Dict[str, Any]:
        """
        Executes the provided circuit on the simulator and returns result histogram.
        """
        logging.info(f"Executing quantum circuit with {repetitions} repetitions...")
        try:
            result = self.simulator.run(circuit, repetitions=repetitions)
            
            # Find the measurement keys inside the circuit
            measurement_keys = list(result.measurements.keys())
            
            if not measurement_keys:
                raise ValueError("No measurement gates found in the circuit.")
            
            # Extract first measurement key (typically 'm')
            key = measurement_keys[0]
            counts = result.histogram(key=key)
            
            # Format integer state representations into binary string keys
            qubits = sorted(list(circuit.all_qubits()))
            qubit_count = len(qubits)
            
            histogram_bitstrings = {}
            for int_state, count in counts.items():
                binary_str = format(int_state, f'0{qubit_count}b')
                histogram_bitstrings[binary_str] = int(count)

            execution_summary = {
                "success": True,
                "repetitions": repetitions,
                "raw_counts": {str(k): int(v) for k, v in counts.items()},
                "bitstring_counts": histogram_bitstrings,
                "dominant_state": max(histogram_bitstrings, key=histogram_bitstrings.get),
                "dominant_probability": float(max(counts.values()) / repetitions)
            }
            logging.info(f"Quantum execution complete. Dominant state: {execution_summary['dominant_state']} "
                         f"({execution_summary['dominant_probability']:.1%})")
            return execution_summary
            
        except Exception as e:
            logging.error(f"Quantum execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "bitstring_counts": {},
                "dominant_state": "00",
                "dominant_probability": 0.0
            }
