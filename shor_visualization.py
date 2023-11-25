import os
import numpy as np
from qiskit.circuit import ControlledGate
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT

np.random.seed(14)

def calculate_shor_params(search: int) -> tuple[int, int, int]:
    n = int(np.ceil(np.log2(search)))
    a = np.random.randint(2, search - 1)
    while np.gcd(a, search) != 1:
        a = np.random.randint(2, search - 1)

    return n, n, a

def get_u_door(base: int, itt_count: int, num_qubits: int, search: int) -> ControlledGate:
    U = QuantumCircuit(num_qubits)
    for _ in range(2 ** itt_count):
        for swap in [(2, 3), (1, 2), (0, 1)]:
            U.swap(*swap)

        U.x(0)

    U = U.to_gate()
    U.name = f'{base}^(2^{itt_count}) mod {search}'
    return U.control()

def shors_algorithm(n: int, m: int, a: int, search: int):
    qc = QuantumCircuit(n + m, n)
    n_range = np.arange(n)
    qc.h(n_range)
    qc.x(n+m-1)

    qc.barrier()

    for itt in n_range[::-1]:
        qc.append(get_u_door(a, itt, n, search), [itt, *list(range(n, n + m))])

    qc.barrier()

    qc.append(QFT(len(range(n)), do_swaps=False).inverse(), range(n))
    qc.measure(n_range, n_range)
    return qc


search_list = [15, 21, 35, 65, 391]
for file_path in [f'./circuits/shor_{s}.png' for s in search_list]:
    if os.path.exists(file_path):
        os.remove(file_path)

for search in search_list:
    n, m, a = calculate_shor_params(search)
    circuit = shors_algorithm(n, m, a, search)
    simulator = Aer.get_backend('qasm_simulator')
    qresult = execute(circuit, backend=simulator, shots=1000).result().get_counts(circuit)

    found_factors = set()
    for res in qresult:
        measured_value = int(res[::-1], 2)
        x = int(np.uint64((a ** (measured_value // 2)) % search))
        gcd_1 = np.gcd(x + 1, search)
        gcd_2 = np.gcd(x - 1, search)
        if gcd_1 not in [1, search] and gcd_2 not in [1, search]:
            found_factors |= {gcd_1, gcd_2}

    if found_factors:
        factors = [x for x in found_factors]
        factors.sort()
        print(f'Search: {search}: factors: {tuple(factors)}')
        fig = circuit.draw(output='mpl', filename=f'./circuits/shor_{search}.png')
