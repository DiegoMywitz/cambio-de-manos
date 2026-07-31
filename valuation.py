"""Estimador orientativo de valor de negocio, por múltiplo de ganancia anual según rubro.

Los múltiplos son aproximaciones de mercado típicas para pymes/fondos de comercio
en Argentina, no un peritaje profesional. Sirven como punto de partida para que
el vendedor tenga una referencia antes de fijar un precio de venta.
"""

# (multiplo_minimo, multiplo_maximo) sobre la ganancia/resultado ANUAL.
MULTIPLOS_POR_RUBRO = {
    "Gastronomía": (1.5, 2.5),
    "Comercio minorista": (1.5, 2.5),
    "Indumentaria": (1.5, 2.5),
    "Servicios": (2.0, 3.0),
    "Industria / Fábrica": (2.5, 4.0),
    "Salud y belleza": (2.0, 3.0),
    "Tecnología": (3.0, 5.0),
    "Educación": (2.0, 3.0),
    "Inmobiliario": (2.0, 3.5),
    "Transporte y logística": (2.0, 3.0),
    "Agropecuario": (2.5, 4.0),
    "Otro": (2.0, 3.0),
}


def estimar_valor(rubro: str, resultado_mensual: float):
    """Devuelve (valor_min, valor_max, mult_min, mult_max) o None si falta el dato de ganancia."""
    if not resultado_mensual or resultado_mensual <= 0:
        return None
    mult_min, mult_max = MULTIPLOS_POR_RUBRO.get(rubro, MULTIPLOS_POR_RUBRO["Otro"])
    ganancia_anual = resultado_mensual * 12
    return ganancia_anual * mult_min, ganancia_anual * mult_max, mult_min, mult_max
