import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="2.1 · Construir circuitos")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Statevector
    from qiskit.primitives import StatevectorSampler

    def veredicto(ok, si, no):
        return mo.callout(mo.md(("✅ " + si) if ok else ("❌ " + no)), kind="success" if ok else "warn")

    mo.md("""
    # 2.1 · Construir circuitos: práctica

    Tres misiones sobre lo que acabas de ver: la lista de instrucciones, la profundidad
    y los circuitos con parámetros. Busca el ✅ en cada una.
    """)
    return Parameter, QuantumCircuit, Statevector, StatevectorSampler, mo, np, veredicto


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟢 Reproduce: un circuito por dentro

    Ejecuta la celda y lee la salida: cada elemento de `qc.data` es una instrucción con su
    operación y sus qubits. Antes de mirar `depth()`, predice cuánto valdrá.
    """)
    return


@app.cell
def _(QuantumCircuit):
    qc = QuantumCircuit(3)
    qc.h(0)
    qc.x(1)
    qc.cx(0, 1)
    qc.z(2)
    qc.h(1)

    for inst in qc.data:
        print(inst.operation.name, [qc.find_bit(q).index for q in inst.qubits])
    print("profundidad:", qc.depth())
    return (qc,)


@app.cell(hide_code=True)
def _(mo, qc):
    mo.vstack([mo.md("Así se ve (cada columna es una capa):"), qc.draw("mpl")])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟡 Modifica: un GHZ menos profundo

    La «escalera» de CNOTs prepara un GHZ de 6 qubits con profundidad **6**: cada CNOT
    espera a la anterior. Reordénala para preparar **el mismo estado** con profundidad
    **4 o menos**. Pista: cuando un qubit ya está entrelazado, también puede hacer de control.
    """)
    return


@app.cell
def _(QuantumCircuit):
    ghz6 = QuantumCircuit(6)
    ghz6.h(0)
    # ✏️ cambia esta escalera por algo más rápido
    for k in range(5):
        ghz6.cx(k, k + 1)
    ghz6.draw("mpl")
    return (ghz6,)


@app.cell(hide_code=True)
def _(QuantumCircuit, Statevector, ghz6, veredicto):
    _ref = QuantumCircuit(6)
    _ref.h(0)
    for _k in range(5):
        _ref.cx(_k, _k + 1)
    _mismo = Statevector(ghz6).equiv(Statevector(_ref))
    veredicto(_mismo and ghz6.depth() <= 4,
              f"Mismo estado GHZ con profundidad {ghz6.depth()}. ¡Un tercio menos de tiempo!",
              f"Profundidad {ghz6.depth()}, mismo estado: {'sí' if _mismo else 'no'}. Busca profundidad ≤ 4 sin cambiar el estado.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🔴 Crea: una familia de circuitos con un parámetro

    1. Construye **una sola vez** un circuito de 2 qubits con un `Parameter` llamado `θ`:
       `rx(θ)` sobre el qubit 0, una `cx(0, 1)` y `measure_all()`.
    2. Con `assign_parameters`, genera la lista `familia` de **21 circuitos** con θ de 0 a π
       (usa `np.linspace(0, np.pi, 21)`).

    La comprobación mide la probabilidad de `11` en cada uno y la compara con la teoría,
    $\\sin^2(θ/2)$.
    """)
    return


@app.cell
def _(Parameter, QuantumCircuit, np):
    theta = Parameter("θ")
    base = QuantumCircuit(2)
    # ✏️ construye el circuito con theta

    familia = []   # ✏️ 21 circuitos con θ asignado
    len(familia)
    return base, familia


@app.cell(hide_code=True)
def _(StatevectorSampler, familia, mo, np, veredicto):
    _ok = len(familia) == 21 and all(c.num_parameters == 0 for c in familia)
    _p = []
    if _ok:
        _res = StatevectorSampler(seed=1).run(familia, shots=4000).result()
        _p = [r.data.meas.get_counts().get("11", 0) / 4000 for r in _res]
        _teo = np.sin(np.linspace(0, np.pi, 21) / 2) ** 2
        _ok = bool(np.max(np.abs(np.array(_p) - _teo)) < 0.05)
    _v = veredicto(_ok, "Las 21 variantes siguen $\\sin^2(θ/2)$: un solo circuito, muchas ejecuciones.",
                   "Necesito 21 circuitos sin parámetros libres cuya probabilidad de `11` siga $\\sin^2(θ/2)$.")
    if _p:
        import matplotlib.pyplot as plt
        _fig, _ax = plt.subplots(figsize=(6, 3))
        _x = np.linspace(0, np.pi, 21)
        _ax.plot(_x, np.sin(_x / 2) ** 2, label="teoría")
        _ax.plot(_x, _p, "o", label="muestreo")
        _ax.set_xlabel("θ"); _ax.set_ylabel("P(11)"); _ax.legend()
        _v = mo.vstack([_v, _fig])
    _v
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    **Para pensar:** en el proyecto Ising cada paso de tiempo es el mismo circuito con otro
    ángulo. ¿Cómo combinarías `compose` y `Parameter` para construir 10 pasos sin escribir
    10 circuitos a mano?
    """)
    return


if __name__ == "__main__":
    app.run()
