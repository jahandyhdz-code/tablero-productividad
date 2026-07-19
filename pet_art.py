"""
pet_art.py — SVG art para cada animal en cada etapa.
Cada entrada es un SVG inline listo para usar en templates con | safe.
"""

# Paletas por animal
_PAL = {
    "perro":   {"base":"#C8956C","oscuro":"#8B5E3C","accent":"#FF9E80","ojo":"#3D1C02"},
    "gato":    {"base":"#A0A0B0","oscuro":"#606070","accent":"#FFB6C1","ojo":"#2E8B57"},
    "conejo":  {"base":"#F0E0D0","oscuro":"#D4A0A0","accent":"#FF9EAA","ojo":"#8B3A8B"},
    "pollito": {"base":"#FFD966","oscuro":"#E6A800","accent":"#FF8C42","ojo":"#222222"},
    "oso":     {"base":"#8B6914","oscuro":"#5C4009","accent":"#D4956A","ojo":"#1A1A1A"},
    "dragon":  {"base":"#4CAF50","oscuro":"#2E7D32","accent":"#FF5722","ojo":"#FFD700"},
}


def _egg(pal: dict) -> str:
    """Huevo con color del animal."""
    b, o, a = pal["base"], pal["oscuro"], pal["accent"]
    return f"""<svg viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">
  <defs><radialGradient id="eg" cx="40%" cy="35%"><stop offset="0%" stop-color="#fff" stop-opacity=".45"/>
  <stop offset="100%" stop-color="{b}"/></radialGradient></defs>
  <ellipse cx="50" cy="60" rx="34" ry="42" fill="url(#eg)" stroke="{o}" stroke-width="2"/>
  <ellipse cx="40" cy="45" rx="6" ry="7" fill="white" fill-opacity=".5"/>
  <ellipse cx="38" cy="43" rx="3" ry="3.5" fill="{a}" fill-opacity=".6"/>
</svg>"""


def _perro_bebe() -> str:
    p = _PAL["perro"]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="64" rx="26" ry="18" fill="{p['oscuro']}" opacity=".15"/>
  <ellipse cx="28" cy="42" rx="11" ry="18" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="72" cy="42" rx="11" ry="18" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="50" cy="50" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="40" cy="47" r="5" fill="white"/>
  <circle cx="60" cy="47" r="5" fill="white"/>
  <circle cx="41" cy="47" r="3" fill="{p['ojo']}"/>
  <circle cx="61" cy="47" r="3" fill="{p['ojo']}"/>
  <circle cx="42" cy="46" r="1" fill="white"/>
  <circle cx="62" cy="46" r="1" fill="white"/>
  <ellipse cx="50" cy="60" rx="9" ry="6" fill="{p['accent']}"/>
  <ellipse cx="50" cy="59" rx="6" ry="3.5" fill="{p['accent']}" opacity=".7"/>
  <path d="M44 63 Q50 68 56 63" fill="#FF6B6B" stroke="#CC4444" stroke-width="1"/>
</svg>"""


def _perro_joven() -> str:
    p = _PAL["perro"]
    return f"""<svg viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="125" rx="30" ry="8" fill="{p['oscuro']}" opacity=".15"/>
  <ellipse cx="26" cy="38" rx="10" ry="17" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="74" cy="38" rx="10" ry="17" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="50" cy="48" r="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <rect x="26" y="70" width="48" height="44" rx="16" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="39" cy="45" r="4.5" fill="white"/>
  <circle cx="61" cy="45" r="4.5" fill="white"/>
  <circle cx="40" cy="45" r="2.8" fill="{p['ojo']}"/>
  <circle cx="62" cy="45" r="2.8" fill="{p['ojo']}"/>
  <circle cx="41" cy="44" r="1" fill="white"/>
  <ellipse cx="50" cy="57" rx="8" ry="5" fill="{p['accent']}"/>
  <path d="M44 60 Q50 65 56 60" fill="#FF6B6B" stroke="#CC4444" stroke-width="1"/>
  <line x1="30" y1="84" x2="30" y2="114" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="70" y1="84" x2="70" y2="114" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <path d="M70 88 Q84 82 82 70" fill="none" stroke="{p['base']}" stroke-width="5" stroke-linecap="round"/>
</svg>"""


def _perro_adulto() -> str:
    p = _PAL["perro"]
    return f"""<svg viewBox="0 0 120 150" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="60" cy="146" rx="38" ry="9" fill="{p['oscuro']}" opacity=".18"/>
  <ellipse cx="28" cy="42" rx="13" ry="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="92" cy="42" rx="13" ry="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="60" cy="55" r="32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <rect x="28" y="82" width="64" height="52" rx="20" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <circle cx="46" cy="51" r="6" fill="white"/>
  <circle cx="74" cy="51" r="6" fill="white"/>
  <circle cx="47" cy="51" r="3.5" fill="{p['ojo']}"/>
  <circle cx="75" cy="51" r="3.5" fill="{p['ojo']}"/>
  <circle cx="48" cy="50" r="1.2" fill="white"/>
  <ellipse cx="60" cy="65" rx="11" ry="7" fill="{p['accent']}"/>
  <ellipse cx="55" cy="65" rx="3" ry="2" fill="white" opacity=".5"/>
  <path d="M51 70 Q60 77 69 70" fill="#FF6B6B" stroke="#CC4444" stroke-width="1.5"/>
  <line x1="36" y1="98" x2="34" y2="138" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <line x1="84" y1="98" x2="86" y2="138" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <path d="M86 108 Q104 98 102 80" fill="none" stroke="{p['base']}" stroke-width="6" stroke-linecap="round"/>
  <ellipse cx="60" cy="93" rx="18" ry="12" fill="{p['oscuro']}" opacity=".25"/>
</svg>"""


def _gato_bebe() -> str:
    p = _PAL["gato"]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="64" rx="26" ry="18" fill="{p['oscuro']}" opacity=".12"/>
  <polygon points="22,44 30,20 40,42" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="60,42 70,20 78,44" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="25,42 30,26 37,42" fill="{p['accent']}"/>
  <polygon points="63,42 70,26 75,42" fill="{p['accent']}"/>
  <circle cx="50" cy="52" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="40" cy="48" rx="5" ry="6" fill="white"/>
  <ellipse cx="60" cy="48" rx="5" ry="6" fill="white"/>
  <ellipse cx="40" cy="49" rx="2.5" ry="4" fill="{p['ojo']}"/>
  <ellipse cx="60" cy="49" rx="2.5" ry="4" fill="{p['ojo']}"/>
  <circle cx="41" cy="47" r="1" fill="white"/>
  <circle cx="61" cy="47" r="1" fill="white"/>
  <ellipse cx="50" cy="61" rx="4" ry="3" fill="{p['accent']}"/>
  <line x1="30" y1="59" x2="10" y2="55" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="30" y1="62" x2="10" y2="62" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="70" y1="59" x2="90" y2="55" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="70" y1="62" x2="90" y2="62" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
</svg>"""


def _gato_joven() -> str:
    p = _PAL["gato"]
    return f"""<svg viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <polygon points="24,40 32,16 42,40" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="58,40 68,16 76,40" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="27,39 32,22 39,39" fill="{p['accent']}"/>
  <polygon points="61,39 68,22 73,39" fill="{p['accent']}"/>
  <circle cx="50" cy="48" r="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <rect x="26" y="70" width="48" height="44" rx="16" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="39" cy="46" rx="4.5" ry="5.5" fill="white"/>
  <ellipse cx="61" cy="46" rx="4.5" ry="5.5" fill="white"/>
  <ellipse cx="39" cy="47" rx="2.2" ry="3.8" fill="{p['ojo']}"/>
  <ellipse cx="61" cy="47" rx="2.2" ry="3.8" fill="{p['ojo']}"/>
  <ellipse cx="50" cy="57" rx="4" ry="3" fill="{p['accent']}"/>
  <line x1="26" y1="57" x2="8" y2="53" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="26" y1="60" x2="8" y2="60" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="74" y1="57" x2="92" y2="53" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="74" y1="60" x2="92" y2="60" stroke="{p['oscuro']}" stroke-width="1.2" opacity=".7"/>
  <line x1="36" y1="70" x2="36" y2="114" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="64" y1="70" x2="64" y2="114" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <path d="M64 80 Q80 70 76 58" fill="none" stroke="{p['base']}" stroke-width="4" stroke-linecap="round"/>
</svg>"""


def _gato_adulto() -> str:
    p = _PAL["gato"]
    return f"""<svg viewBox="0 0 120 150" xmlns="http://www.w3.org/2000/svg">
  <polygon points="26,46 36,16 48,46" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <polygon points="72,46 84,16 94,46" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <polygon points="29,44 36,22 45,44" fill="{p['accent']}"/>
  <polygon points="75,44 84,22 91,44" fill="{p['accent']}"/>
  <circle cx="60" cy="58" r="32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <rect x="30" y="84" width="60" height="52" rx="18" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <ellipse cx="46" cy="54" rx="6" ry="7" fill="white"/>
  <ellipse cx="74" cy="54" rx="6" ry="7" fill="white"/>
  <ellipse cx="46" cy="55" rx="2.8" ry="5" fill="{p['ojo']}"/>
  <ellipse cx="74" cy="55" rx="2.8" ry="5" fill="{p['ojo']}"/>
  <circle cx="47" cy="53" r="1.2" fill="white"/>
  <ellipse cx="60" cy="68" rx="5" ry="4" fill="{p['accent']}"/>
  <line x1="32" y1="66" x2="8" y2="60" stroke="{p['oscuro']}" stroke-width="1.5" opacity=".7"/>
  <line x1="32" y1="70" x2="8" y2="70" stroke="{p['oscuro']}" stroke-width="1.5" opacity=".7"/>
  <line x1="88" y1="66" x2="112" y2="60" stroke="{p['oscuro']}" stroke-width="1.5" opacity=".7"/>
  <line x1="88" y1="70" x2="112" y2="70" stroke="{p['oscuro']}" stroke-width="1.5" opacity=".7"/>
  <line x1="42" y1="90" x2="40" y2="136" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <line x1="78" y1="90" x2="80" y2="136" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <path d="M80 100 Q102 86 98 68" fill="none" stroke="{p['base']}" stroke-width="6" stroke-linecap="round"/>
</svg>"""


def _conejo_bebe() -> str:
    p = _PAL["conejo"]
    return f"""<svg viewBox="0 0 100 110" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="35" cy="32" rx="9" ry="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="65" cy="32" rx="9" ry="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="35" cy="32" rx="5" ry="17" fill="{p['accent']}"/>
  <ellipse cx="65" cy="32" rx="5" ry="17" fill="{p['accent']}"/>
  <circle cx="50" cy="65" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="39" cy="60" r="5.5" fill="white"/>
  <circle cx="61" cy="60" r="5.5" fill="white"/>
  <circle cx="39" cy="61" r="3.2" fill="{p['ojo']}"/>
  <circle cx="61" cy="61" r="3.2" fill="{p['ojo']}"/>
  <circle cx="40" cy="60" r="1.2" fill="white"/>
  <circle cx="62" cy="60" r="1.2" fill="white"/>
  <ellipse cx="50" cy="72" rx="4" ry="3" fill="{p['accent']}"/>
  <path d="M45 76 Q50 80 55 76" fill="none" stroke="{p['oscuro']}" stroke-width="1.2"/>
</svg>"""


def _conejo_joven() -> str:
    p = _PAL["conejo"]
    return f"""<svg viewBox="0 0 100 140" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="34" cy="30" rx="9" ry="24" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="66" cy="30" rx="9" ry="24" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="34" cy="30" rx="5" ry="19" fill="{p['accent']}"/>
  <ellipse cx="66" cy="30" rx="5" ry="19" fill="{p['accent']}"/>
  <circle cx="50" cy="58" r="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <rect x="28" y="80" width="44" height="44" rx="18" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="40" cy="55" r="5" fill="white"/>
  <circle cx="60" cy="55" r="5" fill="white"/>
  <circle cx="40" cy="56" r="3" fill="{p['ojo']}"/>
  <circle cx="60" cy="56" r="3" fill="{p['ojo']}"/>
  <circle cx="41" cy="55" r="1" fill="white"/>
  <ellipse cx="50" cy="66" rx="4" ry="3" fill="{p['accent']}"/>
  <path d="M45 70 Q50 74 55 70" fill="none" stroke="{p['oscuro']}" stroke-width="1.2"/>
  <line x1="33" y1="80" x2="32" y2="124" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="67" y1="80" x2="68" y2="124" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
</svg>"""


def _conejo_adulto() -> str:
    p = _PAL["conejo"]
    return f"""<svg viewBox="0 0 120 160" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="40" cy="32" rx="11" ry="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="80" cy="32" rx="11" ry="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="40" cy="32" rx="6" ry="22" fill="{p['accent']}"/>
  <ellipse cx="80" cy="32" rx="6" ry="22" fill="{p['accent']}"/>
  <circle cx="60" cy="68" r="30" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <rect x="32" y="92" width="56" height="54" rx="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <circle cx="47" cy="63" r="6.5" fill="white"/>
  <circle cx="73" cy="63" r="6.5" fill="white"/>
  <circle cx="47" cy="64" r="3.8" fill="{p['ojo']}"/>
  <circle cx="73" cy="64" r="3.8" fill="{p['ojo']}"/>
  <circle cx="48" cy="63" r="1.5" fill="white"/>
  <ellipse cx="60" cy="77" rx="5" ry="4" fill="{p['accent']}"/>
  <path d="M53 82 Q60 87 67 82" fill="none" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <line x1="38" y1="96" x2="36" y2="146" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <line x1="82" y1="96" x2="84" y2="146" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <ellipse cx="60" cy="115" rx="22" ry="14" fill="{p['oscuro']}" opacity=".15"/>
</svg>"""


def _pollito_bebe() -> str:
    p = _PAL["pollito"]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="50" cy="64" rx="26" ry="18" fill="{p['oscuro']}" opacity=".12"/>
  <circle cx="50" cy="52" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="32" cy="56" rx="10" ry="8" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="68" cy="56" rx="10" ry="8" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="40" cy="46" r="5" fill="white"/>
  <circle cx="60" cy="46" r="5" fill="white"/>
  <circle cx="41" cy="47" r="3.2" fill="{p['ojo']}"/>
  <circle cx="61" cy="47" r="3.2" fill="{p['ojo']}"/>
  <circle cx="42" cy="46" r="1.2" fill="white"/>
  <polygon points="50,56 44,62 56,62" fill="{p['accent']}"/>
  <ellipse cx="50" cy="32" rx="8" ry="6" fill="{p['accent']}" opacity=".8"/>
</svg>"""


def _pollito_joven() -> str:
    p = _PAL["pollito"]
    return f"""<svg viewBox="0 0 100 120" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="44" r="24" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="50" cy="85" rx="22" ry="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="22" cy="80" rx="12" ry="9" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <ellipse cx="78" cy="80" rx="12" ry="9" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="40" cy="40" r="4.5" fill="white"/>
  <circle cx="60" cy="40" r="4.5" fill="white"/>
  <circle cx="41" cy="41" r="2.8" fill="{p['ojo']}"/>
  <circle cx="61" cy="41" r="2.8" fill="{p['ojo']}"/>
  <polygon points="50,50 43,57 57,57" fill="{p['accent']}"/>
  <ellipse cx="50" cy="24" rx="8" ry="6" fill="{p['accent']}" opacity=".9"/>
  <line x1="28" y1="108" x2="22" y2="116" stroke="{p['oscuro']}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="34" y1="110" x2="30" y2="118" stroke="{p['oscuro']}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="72" y1="108" x2="78" y2="116" stroke="{p['oscuro']}" stroke-width="2.5" stroke-linecap="round"/>
  <line x1="66" y1="110" x2="70" y2="118" stroke="{p['oscuro']}" stroke-width="2.5" stroke-linecap="round"/>
</svg>"""


def _pollito_adulto() -> str:
    p = _PAL["pollito"]
    return f"""<svg viewBox="0 0 120 150" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="60" cy="42" rx="6" ry="9" fill="{p['accent']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="60" cy="55" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <ellipse cx="60" cy="108" rx="28" ry="32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <ellipse cx="22" cy="100" rx="16" ry="12" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="98" cy="100" rx="16" ry="12" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="47" cy="50" r="6" fill="white"/>
  <circle cx="73" cy="50" r="6" fill="white"/>
  <circle cx="48" cy="51" r="3.5" fill="{p['ojo']}"/>
  <circle cx="74" cy="51" r="3.5" fill="{p['ojo']}"/>
  <circle cx="49" cy="50" r="1.4" fill="white"/>
  <polygon points="60,62 51,70 69,70" fill="{p['accent']}"/>
  <line x1="36" y1="138" x2="28" y2="148" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="44" y1="140" x2="38" y2="150" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="84" y1="138" x2="92" y2="148" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="76" y1="140" x2="82" y2="150" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
</svg>"""


def _oso_bebe() -> str:
    p = _PAL["oso"]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="28" cy="28" r="14" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="72" cy="28" r="14" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="28" cy="28" r="9" fill="{p['accent']}"/>
  <circle cx="72" cy="28" r="9" fill="{p['accent']}"/>
  <circle cx="50" cy="55" r="30" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="39" cy="50" r="5.5" fill="white"/>
  <circle cx="61" cy="50" r="5.5" fill="white"/>
  <circle cx="40" cy="51" r="3.2" fill="{p['ojo']}"/>
  <circle cx="62" cy="51" r="3.2" fill="{p['ojo']}"/>
  <circle cx="41" cy="50" r="1.2" fill="white"/>
  <ellipse cx="50" cy="63" rx="11" ry="8" fill="{p['accent']}"/>
  <ellipse cx="50" cy="62" rx="7" ry="4.5" fill="{p['oscuro']}" opacity=".4"/>
  <path d="M44 67 Q50 72 56 67" fill="none" stroke="{p['oscuro']}" stroke-width="1.5"/>
</svg>"""


def _oso_joven() -> str:
    p = _PAL["oso"]
    return f"""<svg viewBox="0 0 100 130" xmlns="http://www.w3.org/2000/svg">
  <circle cx="26" cy="26" r="13" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="74" cy="26" r="13" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <circle cx="26" cy="26" r="8" fill="{p['accent']}"/>
  <circle cx="74" cy="26" r="8" fill="{p['accent']}"/>
  <circle cx="50" cy="48" r="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <rect x="24" y="70" width="52" height="48" rx="20" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <ellipse cx="50" cy="82" rx="16" ry="12" fill="{p['accent']}" opacity=".6"/>
  <circle cx="39" cy="45" r="5" fill="white"/>
  <circle cx="61" cy="45" r="5" fill="white"/>
  <circle cx="40" cy="46" r="3" fill="{p['ojo']}"/>
  <circle cx="62" cy="46" r="3" fill="{p['ojo']}"/>
  <ellipse cx="50" cy="57" rx="10" ry="7" fill="{p['accent']}"/>
  <ellipse cx="50" cy="56" rx="6" ry="4" fill="{p['oscuro']}" opacity=".4"/>
  <path d="M44 61 Q50 66 56 61" fill="none" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <line x1="30" y1="70" x2="28" y2="118" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <line x1="70" y1="70" x2="72" y2="118" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
</svg>"""


def _oso_adulto() -> str:
    p = _PAL["oso"]
    return f"""<svg viewBox="0 0 120 150" xmlns="http://www.w3.org/2000/svg">
  <circle cx="28" cy="28" r="17" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="92" cy="28" r="17" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="28" cy="28" r="11" fill="{p['accent']}"/>
  <circle cx="92" cy="28" r="11" fill="{p['accent']}"/>
  <circle cx="60" cy="58" r="32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <rect x="28" y="84" width="64" height="56" rx="24" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <ellipse cx="60" cy="102" rx="22" ry="16" fill="{p['accent']}" opacity=".7"/>
  <circle cx="46" cy="53" r="7" fill="white"/>
  <circle cx="74" cy="53" r="7" fill="white"/>
  <circle cx="47" cy="54" r="4" fill="{p['ojo']}"/>
  <circle cx="75" cy="54" r="4" fill="{p['ojo']}"/>
  <circle cx="48" cy="53" r="1.5" fill="white"/>
  <ellipse cx="60" cy="68" rx="13" ry="9" fill="{p['accent']}"/>
  <ellipse cx="60" cy="67" rx="8" ry="5" fill="{p['oscuro']}" opacity=".4"/>
  <path d="M52 74 Q60 80 68 74" fill="none" stroke="{p['oscuro']}" stroke-width="2"/>
  <line x1="36" y1="88" x2="32" y2="140" stroke="{p['oscuro']}" stroke-width="5" stroke-linecap="round"/>
  <line x1="84" y1="88" x2="88" y2="140" stroke="{p['oscuro']}" stroke-width="5" stroke-linecap="round"/>
</svg>"""


def _dragon_bebe() -> str:
    p = _PAL["dragon"]
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <polygon points="35,30 40,10 45,30" fill="{p['accent']}"/>
  <polygon points="55,30 60,10 65,30" fill="{p['accent']}"/>
  <circle cx="50" cy="55" r="28" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="39" cy="50" r="5.5" fill="#fff9c4"/>
  <circle cx="61" cy="50" r="5.5" fill="#fff9c4"/>
  <ellipse cx="39" cy="51" rx="2.5" ry="3.5" fill="{p['ojo']}"/>
  <ellipse cx="61" cy="51" rx="2.5" ry="3.5" fill="{p['ojo']}"/>
  <circle cx="40" cy="50" r="1" fill="white"/>
  <ellipse cx="50" cy="62" rx="8" ry="5" fill="{p['oscuro']}" opacity=".3"/>
  <path d="M43 65 Q50 70 57 65" fill="none" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="50,44 46,36 54,36" fill="{p['accent']}" opacity=".8"/>
  <ellipse cx="26" cy="60" rx="7" ry="5" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.2"
           transform="rotate(-30 26 60)"/>
  <ellipse cx="74" cy="60" rx="7" ry="5" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.2"
           transform="rotate(30 74 60)"/>
</svg>"""


def _dragon_joven() -> str:
    p = _PAL["dragon"]
    return f"""<svg viewBox="0 0 110 140" xmlns="http://www.w3.org/2000/svg">
  <polygon points="36,34 42,8 48,34" fill="{p['accent']}"/>
  <polygon points="62,34 68,8 74,34" fill="{p['accent']}"/>
  <circle cx="55" cy="50" r="26" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <rect x="28" y="72" width="54" height="50" rx="20" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <circle cx="43" cy="47" r="5" fill="#fff9c4"/>
  <circle cx="67" cy="47" r="5" fill="#fff9c4"/>
  <ellipse cx="43" cy="48" rx="2.4" ry="3.3" fill="{p['ojo']}"/>
  <ellipse cx="67" cy="48" rx="2.4" ry="3.3" fill="{p['ojo']}"/>
  <ellipse cx="55" cy="60" rx="9" ry="6" fill="{p['oscuro']}" opacity=".3"/>
  <path d="M48 64 Q55 70 62 64" fill="none" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <polygon points="55,41 50,33 60,33" fill="{p['accent']}" opacity=".8"/>
  <path d="M6 50 Q14 38 28 50 Q14 62 6 50Z" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <path d="M104 50 Q96 38 82 50 Q96 62 104 50Z" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1.5"/>
  <path d="M72 92 Q90 82 86 68" fill="none" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="34" y1="72" x2="32" y2="122" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
  <line x1="76" y1="72" x2="78" y2="122" stroke="{p['oscuro']}" stroke-width="3" stroke-linecap="round"/>
</svg>"""


def _dragon_adulto() -> str:
    p = _PAL["dragon"]
    return f"""<svg viewBox="0 0 130 160" xmlns="http://www.w3.org/2000/svg">
  <polygon points="44,38 52,8 60,38" fill="{p['accent']}"/>
  <polygon points="70,38 78,8 86,38" fill="{p['accent']}"/>
  <polygon points="58,32 65,12 72,32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="1"/>
  <circle cx="65" cy="62" r="32" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <rect x="34" y="88" width="62" height="58" rx="22" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2.5"/>
  <circle cx="51" cy="58" r="6.5" fill="#fff9c4"/>
  <circle cx="79" cy="58" r="6.5" fill="#fff9c4"/>
  <ellipse cx="51" cy="59" rx="3" ry="4.2" fill="{p['ojo']}"/>
  <ellipse cx="79" cy="59" rx="3" ry="4.2" fill="{p['ojo']}"/>
  <circle cx="52" cy="57" r="1.2" fill="white"/>
  <ellipse cx="65" cy="75" rx="11" ry="7" fill="{p['oscuro']}" opacity=".3"/>
  <path d="M56 80 Q65 87 74 80" fill="none" stroke="{p['oscuro']}" stroke-width="2"/>
  <polygon points="65,50 59,40 71,40" fill="{p['accent']}"/>
  <path d="M4 52 Q16 34 34 52 Q16 70 4 52Z" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <path d="M126 52 Q114 34 96 52 Q114 70 126 52Z" fill="{p['base']}" stroke="{p['oscuro']}" stroke-width="2"/>
  <path d="M6 40 Q16 28 30 48" fill="none" stroke="{p['accent']}" stroke-width="2" opacity=".7"/>
  <path d="M96 108 Q118 94 114 74" fill="none" stroke="{p['oscuro']}" stroke-width="4" stroke-linecap="round"/>
  <line x1="42" y1="92" x2="38" y2="146" stroke="{p['oscuro']}" stroke-width="5" stroke-linecap="round"/>
  <line x1="88" y1="92" x2="92" y2="146" stroke="{p['oscuro']}" stroke-width="5" stroke-linecap="round"/>
  <circle cx="65" cy="62" r="32" fill="none" stroke="{p['ojo']}" stroke-width="1" opacity=".3"/>
</svg>"""


# Mapa completo: ART[animal][stage] -> SVG string
def _build() -> dict:
    d = {}
    for animal, pal in _PAL.items():
        d[animal] = {"huevo": _egg(pal)}
    d["perro"]["bebe"]    = _perro_bebe()
    d["perro"]["joven"]   = _perro_joven()
    d["perro"]["adulto"]  = _perro_adulto()
    d["gato"]["bebe"]     = _gato_bebe()
    d["gato"]["joven"]    = _gato_joven()
    d["gato"]["adulto"]   = _gato_adulto()
    d["conejo"]["bebe"]   = _conejo_bebe()
    d["conejo"]["joven"]  = _conejo_joven()
    d["conejo"]["adulto"] = _conejo_adulto()
    d["pollito"]["bebe"]  = _pollito_bebe()
    d["pollito"]["joven"] = _pollito_joven()
    d["pollito"]["adulto"]= _pollito_adulto()
    d["oso"]["bebe"]      = _oso_bebe()
    d["oso"]["joven"]     = _oso_joven()
    d["oso"]["adulto"]    = _oso_adulto()
    d["dragon"]["bebe"]   = _dragon_bebe()
    d["dragon"]["joven"]  = _dragon_joven()
    d["dragon"]["adulto"] = _dragon_adulto()
    return d

ART = _build()


def get_art(animal: str, stage: str) -> str:
    """Retorna el SVG del animal en la etapa dada. Fallback a huevo."""
    return ART.get(animal, {}).get(stage, ART.get(animal, {}).get("huevo", ""))
