import numpy as np
from qiskit.circuit import ControlledGate
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT

n, m, a = 4, 4, 7
search = 15

def c_amod15(base: int, itt_count: int) -> ControlledGate:
    U = QuantumCircuit(4)
    for _ in range(2 ** itt_count):
        for swap in [(2, 3), (1, 2), (0, 1)]:
            U.swap(*swap)

        for q in range(4):
            U.x(q)

    U = U.to_gate()
    U.name = f'{base}^(2^{itt_count}) mod 15'
    return U.control()

def shors_algorithm(n, m, a):
    qc = QuantumCircuit(n + m, n)
    n_range = np.arange(n)
    qc.h(n_range)
    qc.x(n+m-1)

    qc.barrier()

    for itt in n_range[::-1]:
        qc.append(c_amod15(a, itt), [itt, *list(range(n, n + m))])

    qc.barrier()

    qc.append(QFT(len(range(n)), do_swaps=False).inverse(), range(n))
    qc.measure(n_range, n_range)
    return qc

circuit = shors_algorithm(n, m, a)
simulator = Aer.get_backend('qasm_simulator')
qresult = execute(circuit, backend=simulator, shots=1000).result().get_counts(circuit)
circuit.draw(output='mpl', filename='./shor.png')

for res in qresult:
    measured_value = int(res[::-1], 2)
    x = int((a ** (measured_value / 2)) % search)
    if not (measured_value % 2 != 0 or (x + 1) % search == 0):
        print(np.gcd(x + 1, search), np.gcd(x - 1, search))
