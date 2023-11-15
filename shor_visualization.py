import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT

def initialize_qubits(given_circuit: QuantumCircuit, n: int, m: int) -> None:
    given_circuit.h(range(n))
    given_circuit.x(n+m-1)

def c_amod15(a: int, x: int):
    if a not in [2,7,8,11,13]:
        raise ValueError("'a' must be 2,7,8,11,13")
    U = QuantumCircuit(4)
    for iteration in range(x):
        if a in [2,13]:
            U.swap(0,1)
            U.swap(1,2)
            U.swap(2,3)
        if a in [7,8]:
            U.swap(2,3)
            U.swap(1,2)
            U.swap(0,1)
        if a == 11:
            U.swap(1,3)
            U.swap(0,2)
        if a in [7,11,13]:
            for q in range(4):
                U.x(q)
    U = U.to_gate()
    U.name = "%i^%i mod 15" % (a, x)
    c_U = U.control()
    return c_U

def modular_exponentiation(circuit: QuantumCircuit, n: int, m: int, a):
    for x in range(n):
        exponent = 2 ** x
        circuit.append(c_amod15(a, exponent), [x] + list(range(n, n + m)))

def inverse_qft(circuit, measurement_qubits):
    circuit.append(QFT(len(measurement_qubits), do_swaps=False).inverse(), measurement_qubits)

def shors_algorithm(n, m, a):
    qc = QuantumCircuit(n + m, n)
    initialize_qubits(qc, n, m)
    qc.barrier()

    modular_exponentiation(qc, n, m, a)
    qc.barrier()

    inverse_qft(qc, range(n))
    qc.measure(range(n), range(n))
    return qc

n, m, a = 4, 4, 7
circuit = shors_algorithm(n, m, a)


simulator = Aer.get_backend('qasm_simulator')
counts = execute(circuit, backend=simulator, shots=1000).result().get_counts(circuit)
circuit.draw(output='mpl', filename='./shor.png')