import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", app_title="1.4 · Tu primer circuito")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    from qiskit import QuantumCircuit
    from qiskit.primitives import StatevectorSampler
    from qiskit.visualization import plot_histogram

    def veredicto(ok, si, no):
        """Muestra ✅ o ❌ según la comprobación."""
        return mo.callout(mo.md(("✅ " + si) if ok else ("❌ " + no)), kind="success" if ok else "warn")

    def conteos(qc, shots=1024):
        return StatevectorSampler(seed=7).run([qc], shots=shots).result()[0].data.meas.get_counts()

    mo.md("""
    # 1.4 · Tu primer circuito: práctica

    Tres misiones, de menos a más. Cada una tiene una comprobación que se actualiza sola
    al cambiar el código: busca el ✅.
    """)
    return QuantumCircuit, conteos, mo, plot_histogram, veredicto


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟢 Reproduce: el estado de Bell

    Ejecuta el circuito de la lección y mira los conteos. No tienes que cambiar nada:
    lee cada línea y asegúrate de entender qué hace.
    """)
    return


@app.cell
def _(QuantumCircuit, conteos):
    bell = QuantumCircuit(2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure_all()

    conteos_bell = conteos(bell)
    conteos_bell
    return (conteos_bell,)


@app.cell(hide_code=True)
def _(conteos_bell, veredicto):
    veredicto(set(conteos_bell) == {"00", "11"},
              "Solo aparecen `00` y `11`: los qubits están perfectamente correlacionados.",
              "Deberían aparecer solo `00` y `11`. ¿Cambiaste algo del circuito?")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🟡 Modifica: el otro estado de Bell

    Cambia el circuito para preparar $\\tfrac{1}{\\sqrt2}\\big(|01\\rangle + |10\\rangle\\big)$:
    los dos qubits siempre **distintos**. Pista: basta con añadir **una** puerta.
    """)
    return


@app.cell
def _(QuantumCircuit, conteos):
    anti = QuantumCircuit(2)
    anti.h(0)
    anti.cx(0, 1)
    # ✏️ añade aquí tu puerta
    anti.measure_all()

    conteos_anti = conteos(anti)
    conteos_anti
    return (conteos_anti,)


@app.cell(hide_code=True)
def _(conteos_anti, veredicto):
    veredicto(set(conteos_anti) == {"01", "10"},
              "¡Eso es! Los qubits salen siempre distintos: `01` o `10`.",
              f"Ahora salen {sorted(conteos_anti)}. Busca que solo aparezcan `01` y `10`.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 🔴 Crea: GHZ de $n$ qubits

    Escribe una función `ghz(n)` que devuelva un circuito de `n` qubits, medido con
    `measure_all()`, cuyo resultado sea solo `00…0` o `11…1`. Usa un bucle `for`.
    Luego mueve el control para ver el histograma con distintos tamaños.
    """)
    return


@app.cell
def _(QuantumCircuit):
    def ghz(n):
        qc = QuantumCircuit(n)
        # ✏️ tu código aquí
        qc.measure_all()
        return qc
    return (ghz,)


@app.cell(hide_code=True)
def _(conteos, ghz, veredicto):
    def _ok(n):
        c = conteos(ghz(n))
        return set(c) == {"0" * n, "1" * n}
    veredicto(all(_ok(n) for n in range(2, 7)),
              "Tu `ghz(n)` funciona para n = 2…6.",
              "Para algún n entre 2 y 6 aparecen otras cadenas, o falta alguna de las dos.")
    return


@app.cell(hide_code=True)
def _(mo):
    n_slider = mo.ui.slider(2, 10, value=3, label="número de qubits", show_value=True)
    n_slider
    return (n_slider,)


@app.cell(hide_code=True)
def _(conteos, ghz, n_slider, plot_histogram):
    plot_histogram(conteos(ghz(n_slider.value)))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    **Para pensar:** cuando $n$ crece, ¿tarda más la simulación? ¿Por qué un computador
    clásico tendría problemas con $n = 50$, si el resultado sigue siendo solo dos cadenas?
    """)
    return


if __name__ == "__main__":
    app.run()
