"""Widgets reutilizables para números grandes en pesos argentinos.

st.number_input no soporta separador de miles mientras se escribe (es un
input numérico nativo del navegador). money_input usa un text_input y va
formateando con puntos en cada cambio, para que números grandes (ej.
150.000.000) se puedan leer mientras se cargan.

Solo funciona con reformateo en vivo fuera de un st.form: dentro de un
formulario, Streamlit no dispara on_change hasta que se aprieta el botón de
enviar.
"""

import re

import streamlit as st


def money_input(label: str, key: str, help: str = None) -> float:
    raw_key = f"_moneyraw_{key}"

    def _reformatear():
        digitos = re.sub(r"\D", "", st.session_state.get(raw_key) or "")
        st.session_state[raw_key] = f"{int(digitos):,}".replace(",", ".") if digitos else ""

    st.text_input(label, key=raw_key, on_change=_reformatear, help=help, placeholder="0")
    digitos = re.sub(r"\D", "", st.session_state.get(raw_key) or "")
    return float(digitos) if digitos else 0.0
