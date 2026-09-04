import random

from configuracion import MODO_SIMULACION


def leer_sensores():
    
    #Lee todos los sensores del edificio. Mientras estemos trabajando sin la Raspberry, utiliza valores simulados
    

    if MODO_SIMULACION:
        return leer_sensores_simulados()

    return leer_sensores_reales()


def leer_sensores_simulados():
    # Genera valores de prueba para poder desarrollar el proyecto aunque la Raspberry esté apagada, esto se cambiará 

    temperatura = round(random.uniform(20, 35),1)

    humedad = round(random.uniform(35, 80),1)

    gas = random.randint(100,1000)

    distancia = round(random.uniform(5, 100),1)

    luz = random.randint(0,100)

    return {
        "temperatura": temperatura,
        "humedad": humedad,
        "gas": gas,
        "distancia": distancia,
        "luz": luz
    }


def leer_sensores_reales():
    
    # Configurare cada lectura del sensos, esto lo cambiare 

    raise RuntimeError(
        "Los sensores reales todavía no han sido configurados jejeje"
    )