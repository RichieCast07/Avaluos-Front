"""Estructura base de un avaluo y el ejemplo de Av. Jose Mariano Jimenez 614
(sirve como avaluo de prueba y para validar el calculo contra el Excel)."""
import copy

ELEMENTOS = [
    ("cimientos", "Cimientos"), ("estructura", "Estructura"), ("muros", "Muros"),
    ("entrepisos", "Entrepisos"), ("techos", "Techos"), ("azoteas", "Azoteas"), ("bardas", "Bardas"),
    ("aplanados_int", "Aplanados interiores"), ("aplanados_ext", "Aplanados exteriores"),
    ("techos_acab", "Techos (acabado)"), ("lambrines", "Lambrines"), ("pisos", "Pisos"),
    ("escaleras", "Escaleras"), ("pintura", "Pintura"), ("recubrimientos", "Recubrimientos especiales"),
    ("carpinteria", "Carpintería"), ("hidraulicas", "Instalaciones hidráulicas y sanitarias"),
    ("electricas", "Instalaciones eléctricas"), ("puertas", "Puertas y ventanerías"),
    ("herreria", "Herrería"), ("vidrieria", "Vidriería"), ("cerrajeria", "Cerrajería"),
    ("fachada", "Fachada"), ("especiales", "Instalaciones especiales, accesorios y obras complementarias"),
]

FACTORES_TERRENO = {
    "neg": "Es el factor que a juicio del perito valuador, con base en las observaciones del mercado en operaciones de contado, ajusta al precio de la oferta.",
    "ubic": "Este factor califica la localización física del bien valuado vs. la oferta.",
    "zona": "Factor que se utiliza para valorar según la zona en la que se ubica el inmueble.",
    "forma": "Es el resultado de calificar la irregularidad de la oferta respecto al bien valuado.",
    "sup": "En función de la superficie de la oferta con respecto al bien valuado.",
    "otro": "",
}
FACTORES_INMUEBLES = {
    "neg": "Es el factor que a juicio del perito valuador, con base en las observaciones del mercado en operaciones de contado, ajusta al precio de la oferta.",
    "ubic": "Este factor califica la localización física del bien valuado vs. la oferta.",
    "sup": "En función de la superficie de la oferta con respecto al bien valuado.",
    "calid": "Es el factor que considera las diferencias entre el inmueble a valuar y la oferta, en relación al tipo y calidad de construcción.",
    "edo": "Es el índice que considera el nivel de deterioro que una edificación registra por el mayor o menor mantenimiento que se le ha proporcionado.",
    "otro": "",
}

TEXTO_DECLARACIONES = [
    "El valor comercial del inmueble es de acuerdo a la situación actual del País y a las condiciones y conservación aparente del inmueble. Si se modifica los metros cuadrados del terreno, es necesario elaborar otro avalúo.",
    "Se proporcionó información por parte del propietario la cual fue considerada dentro del presente documento bajo la salvedad de las mismas.",
]


def vacio():
    return {
        "fecha": "",
        "inmueble": {"calle": "", "numero": "", "colonia": "", "municipio": "", "cp": "",
                     "estado": "", "cuenta_predial": "", "cuenta_agua": ""},
        "generales": {"bien": "Terreno y construcción", "regimen": "Particular", "propietario": "",
                      "solicitante": "", "proposito": "Conocer el valor comercial del inmueble",
                      "uso": "Para los intereses que al propietario convengan"},
        "zona": {"construccion_dominante": "", "densidad": "", "contaminacion": "", "uso_suelo": "",
                 "saturacion": "", "vias_acceso": "", "servicios": "", "equipamiento": ""},
        "terreno": {"tramos": "", "escritura": "",
                    "norte": {"medida": "", "colinda": ""}, "sur": {"medida": "", "colinda": ""},
                    "oriente": {"medida": "", "colinda": ""}, "poniente": {"medida": "", "colinda": ""},
                    "superficie": "", "construccion": "", "indiviso": "100",
                    "topografia": "Plano de forma regular", "frentes": "1", "panoramicas": "",
                    "densidad_hab": "Según plan de desarrollo urbano del municipio",
                    "intensidad": "Según plan de desarrollo urbano del municipio",
                    "servidumbre": "", "longitud": "", "latitud": "", "altitud": ""},
        "descripcion": {"uso_actual": "", "tipo1_m2": "", "calidad": "Buena", "niveles": "",
                        "edad": "", "vida_remanente": "", "vida_total": "", "conservacion": "Buena",
                        "unidades_rentables": "1", "elementos": {k: "" for k, _ in ELEMENTOS}},
        "comparables_terreno": {"nivel_oferta": "MEDIA", "items": [
            {"direccion": "", "telefono": "", "liga": "", "sup": "", "oferta": "",
             "neg": "0.98", "ubic": "1", "zona": "1", "forma": "1", "otro": "1"} for _ in range(4)],
            "notas": dict(FACTORES_TERRENO)},
        "costos": {"terreno_coef": "1", "terreno_motivo": "",
                   "construcciones": [{"uso": "", "area": "", "vrn": "", "demerito": ""}],
                   "especiales": []},
        "comparables_inmuebles": {"nivel_oferta": "MEDIA", "monto_adicional": "0", "items": [
            {"direccion": "", "telefono": "", "liga": "", "constr": "", "terreno": "", "oferta": "",
             "neg": "0.95", "ubic": "1", "calid": "1", "edo": "1", "otro": "1"} for _ in range(4)],
            "notas": dict(FACTORES_INMUEBLES)},
        "conclusion": {"valor_conclusion": "mercado", "declaraciones": list(TEXTO_DECLARACIONES),
                       "comentarios": TEXTO_DECLARACIONES[1], "vigencia_meses": "6"},
    }


def ejemplo():
    d = vacio()
    d["fecha"] = "2026-10-15"
    d["inmueble"].update(calle="Av. José Mariano Jiménez", numero="614", colonia="Los Sauces 2° Sector",
                         municipio="San Pedro Garza García", cp="66237", estado="Nuevo León, México.",
                         cuenta_predial="04-065-010", cuenta_agua="")
    d["generales"].update(propietario="Francisco de Sales de la Garza Villarreal")
    d["zona"].update(
        construccion_dominante="Comercios", densidad="Alta",
        contaminacion="Ninguna apreció al momento de la visita", uso_suelo="Habitacional", saturacion="95",
        vias_acceso="El inmueble cuenta con acceso a través de la avenida José Mariano Jiménez, conectando con vialidades secundarias como las calles Emilio Carranza y 5 de Mayo, las cuales facilitan la circulación local y el acceso a las propiedades del sector.",
        servicios="Completos: Agua Potable, Drenaje Sanitario, Red de Electrificación, Gas Natural, Alumbrado Público, Red Telefónica, Sistema de televisión por cable, Pavimento Asfáltico, Guarniciones y banquetas de concreto, Vigilancia pública",
        equipamiento="Nomenclatura y señalización de calles y avenidas, centros comerciales, zona hotelera, transporte urbano")
    d["terreno"].update(
        tramos="Noreste calle 2 de abril; al sureste calle Emilio Carranza; oriente Av. José Mariano Jiménez; Poniente calle Los Rayones",
        escritura="Escritura 9,385; Volumen LII; Libro 5; Foja 192; Ciudad de Monterrey, N.L.; 08 de Noviembre de 1991; Lic. Cruz Cantú Garza; Notaría Pública No. 64",
        norte={"medida": "17.615", "colinda": "lote 9"}, sur={"medida": "17.72", "colinda": "lote 11"},
        oriente={"medida": "8", "colinda": "Av. Jiménez"}, poniente={"medida": "8", "colinda": "lote 12"},
        superficie="141.32", construccion="248", panoramicas="Vista normal hacia calle Av. José Mariano Jiménez",
        densidad_hab="Según plan de desarrollo de San Pedro Garza García, N.L.",
        intensidad="Según plan de desarrollo de San Pedro Garza García, N.L.",
        longitud="100°24'38.92\"O", latitud="25°39'35.39\"N", altitud="662")
    d["descripcion"].update(
        uso_actual="Casa habitación, utilizada como oficina en dos plantas con tres baños dos privados, cochera para dos autos, pasillo lateral y cocineta, sobre avenida comercial.",
        tipo1_m2="248", niveles="2", edad="30", vida_remanente="40", vida_total="70")
    d["descripcion"]["elementos"].update(
        cimientos="Concreto armado en zapatas corridas, vigas de cimentación",
        estructura="Concreto armado en columnas, castillos y cerramientos",
        muros="Block asentado con mezcla de cemento y arena", entrepisos="Losa de concreto armado",
        techos="Losa de concreto armado", azoteas="Impermeabilizante en frío", bardas="",
        aplanados_int="Yeso a regla acabado fino", aplanados_ext="Concreto arena acabado fino",
        techos_acab="Yeso a regla acabado fino", lambrines="Loseta cerámica de buena calidad",
        pisos="Mosaico cerámica esmaltada",
        escaleras="Escaleras de concreto armado con acabado de cemento pulido",
        pintura="Muros con pintura vinílica y acabado texturizado",
        recubrimientos="Loseta cerámica de buena calidad", carpinteria="En puertas",
        hidraulicas="Tuberías ocultas de cobre y PVC hidráulico en diferentes diámetros",
        puertas="De calidad buena", vidrieria="Cristal filtrasol", cerrajeria="Buena calidad con seguro interior",
        fachada="Fachada de líneas rectas con recubrimiento tipo cantera en columnas y marcos de ventanas, con molduras decorativas y acabado de pintura")
    ct = d["comparables_terreno"]
    datos_t = [("Casco Urbano, San Pedro Garza García, N.L.", "81 8709 5807", "251", "7500000"),
               ("La Cima, San Pedro Garza García, N.L.", "81 2350 0733", "570", "16000000"),
               ("Casco Urbano, San Pedro Garza García, N.L.", "81 2397 0228", "544", "14000000"),
               ("Vasconcelos, Casco Urbano, San Pedro Garza García, N.L.", "", "617", "18900000")]
    for it, (dire, tel, sup, of) in zip(ct["items"], datos_t):
        it.update(direccion=dire, telefono=tel, sup=sup, oferta=of)
    ci = d["comparables_inmuebles"]
    datos_i = [("Libertad 237, Casco Urbano, San Pedro Garza García", "81 1504 3516", "271", "182", "9680000"),
               ("Los Sauces, San Pedro Garza García, Nuevo León", "81 8709 3590", "226", "119", "5800000"),
               ("Libertad, San Pedro Garza García Centro, San Pedro Garza García", "8181431003", "270", "183", "9950000"),
               ("Morelos 328, Casco Urbano, San Pedro Garza García, N.L.", "8182724646", "300", "201", "9000000")]
    for it, (dire, tel, c, t, of) in zip(ci["items"], datos_i):
        it.update(direccion=dire, telefono=tel, constr=c, terreno=t, oferta=of)
    d["costos"]["construcciones"] = [{"uso": "OFICINA", "area": "248", "vrn": "17306.73", "demerito": "0.55"}]
    return copy.deepcopy(d)


# Capacidad del formato de Excel de la inmobiliaria (renglones que tiene la plantilla)
MAX_COMPARABLES = 4
MAX_CONSTRUCCIONES = 3
MAX_ESPECIALES = 5
MAX_FOTOS_ANEXO = 6
MAX_EXPERIENCIA = 5
