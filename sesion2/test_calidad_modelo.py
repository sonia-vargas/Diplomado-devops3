"""Quality gate del modelo: exactitud mínima sobre datos que el modelo nunca vio."""

import os

from app.clasificador import Clasificador, cargar_datos

UMBRAL = float(os.environ.get("UMBRAL_EXACTITUD", "0.80"))


def test_exactitud_sobre_datos_de_evaluacion():
    clasificador = Clasificador()
    textos, esperadas = cargar_datos("evaluacion.csv")
    aciertos = sum(
        clasificador.clasificar(texto)["categoria"] == esperada
        for texto, esperada in zip(textos, esperadas, strict=True)
    )
    exactitud = aciertos / len(textos)
    print(f"\nExactitud: {exactitud:.0%} ({aciertos}/{len(textos)}) · umbral: {UMBRAL:.0%}")
    assert exactitud >= UMBRAL, f"Exactitud {exactitud:.0%} por debajo del umbral {UMBRAL:.0%}"
