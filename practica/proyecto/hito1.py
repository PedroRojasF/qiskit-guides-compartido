import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="Proyecto Ising · Hito I")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    from scipy.linalg import expm
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import SparsePauliOp, Operator, Statevector

    def veredicto(ok, si, no):
        return mo.callout(mo.md(("✅ " + si) if ok else ("❌ " + no)), kind="success" if ok else "warn")

    mo.md("""
    # Proyecto Ising · Hito I: dos espines y un paso de tiempo

    A lo largo del curso vas a simular cómo evoluciona una **cadena de espines** después de
    encender de golpe un campo magnético transversal, y terminarás ejecutándolo en un
    computador cuántico real. El modelo es el de Ising con campo transversal:

    $$H = J \\sum_{i} Z_i Z_{i+1} \\; + \\; h \\sum_i X_i$$

    El término $ZZ$ quiere alinear espines vecinos; el término $X$ los hace girar.
    Hoy empezamos con lo mínimo: **2 espines** y **un paso** de tiempo.
    """)
    return Operator, QuantumCircuit, SparsePauliOp, Statevector, expm, mo, np, veredicto


@app.cell(hide_code=True)
def _(mo):
    cuenta = mo.ui.checkbox(label="Creé mi cuenta en IBM Quantum Platform (plan Open) y guardé mi clave de API fuera del código")
    mo.vstack([
        mo.md("""
        ## 🗝️ Preparación: tu cuenta de IBM Quantum

        En el hito V ejecutarás en hardware real. Crea ya tu cuenta gratuita en
        [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com/) (plan Open: 10 minutos de QPU
        cada 28 días). Guarda la clave de API en un lugar seguro; la configurarás en la lección 5.1.
        """),
        cuenta,
    ])
    return (cuenta,)


@app.cell(hide_code=True)
def _(cuenta, mo):
    mo.md("✅ Listo para el hito V." if cuenta.value else "_Marca la casilla cuando la tengas._")
    return


@app.cell(hide_code=True)
def _(mo):
    J = mo.ui.slider(0.0, 2.0, step=0.1, value=1.0, label="J (acoplamiento ZZ)", show_value=True)
    h = mo.ui.slider(0.0, 2.0, step=0.1, value=0.5, label="h (campo transversal)", show_value=True)
    dt = mo.ui.slider(0.01, 1.0, step=0.01, value=0.1, label="dt (paso de tiempo)", show_value=True)
    mo.vstack([mo.md("## Parámetros\nMuévelos cuando termines las misiones y mira qué cambia."), J, h, dt])
    return J, dt, h


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟢 Reproduce: el Hamiltoniano como `SparsePauliOp`

    Recuerda que Qiskit escribe el qubit 0 a la **derecha**: `"IX"` es $X$ sobre el qubit 0.
    """)
    return


@app.cell
def _(J, SparsePauliOp, h):
    H = SparsePauliOp.from_list([
        ("ZZ", J.value),
        ("IX", h.value),
        ("XI", h.value),
    ])
    H
    return (H,)


@app.cell(hide_code=True)
def _(H, veredicto):
    veredicto(H.num_qubits == 2 and len(H) == 3,
              "El Hamiltoniano tiene 2 qubits y 3 términos.",
              "Revisa: deberían ser 2 qubits y 3 términos (ZZ, IX, XI).")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟡 Modifica: un paso de Trotter

    La evolución exacta es $e^{-iH\\,dt}$. Como $ZZ$ y $X$ no conmutan, la aproximamos con un
    **paso de Trotter**: primero el término $ZZ$, después el $X$:

    $$e^{-iH\\,dt} \\approx e^{-i h\\,dt\\,(X_0+X_1)}\\; e^{-i J\\,dt\\,Z_0Z_1}$$

    En Qiskit, `rzz(θ, a, b)` aplica $e^{-i\\frac{θ}{2} Z_aZ_b}$ y `rx(θ, q)` aplica $e^{-i\\frac{θ}{2} X_q}$.
    Completa el circuito con los **ángulos correctos** (ojo con el factor 2).
    """)
    return


@app.cell
def _(J, QuantumCircuit, dt, h):
    paso = QuantumCircuit(2)
    paso.rzz(0.0, 0, 1)   # ✏️ ángulo correcto en función de J.value y dt.value
    paso.rx(0.0, 0)       # ✏️ ángulo correcto en función de h.value y dt.value
    paso.rx(0.0, 1)       # ✏️
    paso.draw("mpl")
    return (paso,)


@app.cell(hide_code=True)
def _(J, Operator, SparsePauliOp, dt, expm, h, paso, veredicto):
    _zz = expm(-1j * J.value * dt.value * SparsePauliOp("ZZ").to_matrix())
    _x = expm(-1j * h.value * dt.value * SparsePauliOp.from_list([("IX", 1), ("XI", 1)]).to_matrix())
    _esperado = Operator(_x @ _zz)
    veredicto(Operator(paso).equiv(_esperado),
              "Tu circuito es exactamente el paso de Trotter.",
              "Todavía no coincide con $e^{-ih\\,dt(X_0+X_1)}e^{-iJ\\,dt\\,Z_0Z_1}$. ¿Usaste el factor 2?")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🔴 Crea: ¿qué tan buena es la aproximación?

    Calcula la **fidelidad** entre el estado tras tu paso de Trotter y el estado exacto,
    partiendo de $|00\\rangle$: $F = |\\langle\\psi_{\\text{exacto}}|\\psi_{\\text{Trotter}}\\rangle|^2$.
    Usa `Statevector.from_instruction(paso)` y `expm(-1j * H.to_matrix() * dt.value)`.
    Guarda el resultado en `fidelidad`.
    """)
    return


@app.cell
def _(H, Statevector, dt, expm, np, paso):
    psi_trotter = Statevector.from_instruction(paso)
    psi_exacto = None   # ✏️ aplica expm(-1j * H.to_matrix() * dt.value) al estado |00⟩
    fidelidad = 0.0     # ✏️
    fidelidad
    return (fidelidad,)


@app.cell(hide_code=True)
def _(H, Statevector, dt, expm, fidelidad, np, paso, veredicto):
    _psi0 = np.zeros(4); _psi0[0] = 1
    _ref = abs(np.vdot(expm(-1j * H.to_matrix() * dt.value) @ _psi0, Statevector.from_instruction(paso).data)) ** 2
    veredicto(abs(float(fidelidad) - _ref) < 1e-6,
              f"Fidelidad = {_ref:.6f}. Ahora mueve **dt**: ¿cómo cae la fidelidad al agrandar el paso?",
              "La fidelidad no coincide todavía. Revisa el estado inicial y el módulo al cuadrado.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    **Para pensar:** si $J = 0$ o $h = 0$, ¿cuánto vale la fidelidad, y por qué?
    En el hito II encadenarás muchos pasos para llegar a tiempos largos.
    """)
    return


if __name__ == "__main__":
    app.run()
