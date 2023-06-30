from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, execute
from qiskit.providers.aer import AerSimulator
from math import pi
from fractions import Fraction

# Function def qc_mod15
def qc_mod15(a, power, show=False):
    assert a in [2, 4, 7, 8, 11, 13], 'Invalid value of argument a:' + str(a)
    qrt = QuantumRegister(4, 'target')
    U = QuantumCircuit(qrt)
    for i in range(power):
        if a in [2, 13]:
            U.swap(0, 1)
            U.swap(1, 2)
            U.swap(2, 3)
        if a in [7, 8]:
            U.swap(2, 3)
            U.swap(1, 2)
            U.swap(0, 1)
        if a in [4, 11]:
            U.swap(1, 3)
            U.swap(0, 2)
        if a in [7, 11, 13]:
            for j in range(4):
                U.x(j)
    if show:
        print('Below is the circuit of U of ' + f'"{a}^{power} mod15":')
        display(U.draw('mpl'))
    U = U.to_gate()
    U.name = f'"{a}^{power} mod15'
    C_U = U.control()
    return C_U

# Function def iqft
def iqft(n):
    br = QuantumRegister(n, 'b')
    qc = QuantumCircuit(br)
    for sbit in range(n//2):
        qc.swap(sbit, n-sbit-1)
    for hbit in range(0, n, 1):
        for cbit in range(hbit-1, -1, -1):
            qc.cp(-pi/2**(hbit-cbit), cbit, hbit)
        qc.h(hbit)
    return qc

# Function def qpf15
def qpf15(count_no, a):
    qrc = QuantumRegister(count_no, 'count')
    # Input of qc_mod15 gate
    qry = QuantumRegister(4, 'y')
    clr = ClassicalRegister(count_no, 'c')
    qc = QuantumCircuit(qrc, qry, clr)
    for cbit in range(count_no):
        qc.h(cbit)
    qc.x(qry[0])
    for cbit in range(count_no):
        qc.append(qc_mod15(a, 2**cbit), [cbit] + list(range(count_no, count_no+4)))
    qc.append(iqft(count_no).to_gate(label='IQFT'), range(count_no))
    qc.measure(range(count_no), range(count_no))
    return qc

# Main code
input_data = int(input())
input_list = []
for i in range(input_data):
    input_string = input("")
    input_list.append(list(map(int, input_string.split())))

output_list = []

for input_values in input_list:
    input_count_no = input_values[0]
    input_a = input_values[1]
    qc = qpf15(input_count_no, input_a)
    sim = AerSimulator()
    job = execute(qc, backend=sim, shots=1000)
    result = job.result()
    counts = result.get_counts(qc)
    
    for akey in counts.keys():
        dec = int(akey, base=2)
        period = Fraction(dec / (2 ** input_count_no)).limit_denominator(15)
        output_list.append((akey, period, input_values))

# Sort the output list based on the order of the input and the akey
output_list = sorted(output_list, key=lambda x: (input_list.index(x[2]), x[0]))

# Print the sorted output
for item in output_list:
    akey = item[0]
    period = item[1]
    print(f"{akey} {period.denominator}")