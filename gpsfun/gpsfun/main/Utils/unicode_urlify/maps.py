"""
urlify maps
"""

latin_map = {
    u'À': u'A', u'Á': u'A', u'Â': u'A', u'Ã': u'A', u'Ä': u'A', u'Å': u'A', u'Æ': u'AE', u'Ç':
    u'C', u'È': u'E', u'É': u'E', u'Ê': u'E', u'Ë': u'E', u'Ì': u'I', u'Í': u'I', u'Î': u'I',
    u'Ï': u'I', u'Ð': u'D', u'Ñ': u'N', u'Ò': u'O', u'Ó': u'O', u'Ô': u'O', u'Õ': u'O', u'Ö':
    u'O', u'Ő': u'O', u'Ø': u'O', u'Ù': u'U', u'Ú': u'U', u'Û': u'U', u'Ü': u'U', u'Ű': u'U',
    u'Ý': u'Y', u'Þ': u'TH', u'ß': u'ss', u'à': u'a', u'á': u'a', u'â': u'a', u'ã': u'a', u'ä':
    u'a', u'å': u'a', u'æ': u'ae', u'ç': u'c', u'è': u'e', u'é': u'e', u'ê': u'e', u'ë': u'e',
    u'ì': u'i', u'í': u'i', u'î': u'i', u'ï': u'i', u'ð': u'd', u'ñ': u'n', u'ò': u'o', u'ó':
    u'o', u'ô': u'o', u'õ': u'o', u'ö': u'o', u'ő': u'o', u'ø': u'o', u'ù': u'u', u'ú': u'u',
    u'û': u'u', u'ü': u'u', u'ű': u'u', u'ý': u'y', u'þ': u'th', u'ÿ': u'y'
}

latin_symbol_map = {
    u'©': u'c'
}

greek_map = {
    u'α': u'a', u'β': u'b', u'γ': u'g', u'δ': u'd', u'ε': u'e', u'ζ': u'z', u'η': u'h', u'θ': u'8',
    u'ι': u'i', u'κ': u'k', u'λ': u'l', u'μ': u'm', u'ν': u'n', u'ξ': u'3', u'ο': u'o', u'π': u'p',
    u'ρ': u'r', u'σ': u's', u'τ': u't', u'υ': u'y', u'φ': u'f', u'χ': u'x', u'ψ': u'ps', u'ω': u'w',
    u'ά': u'a', u'έ': u'e', u'ί': u'i', u'ό': u'o', u'ύ': u'y', u'ή': u'h', u'ώ': u'w', u'ς': u's',
    u'ϊ': u'i', u'ΰ': u'y', u'ϋ': u'y', u'ΐ': u'i',
    u'Α': u'A', u'Β': u'B', u'Γ': u'G', u'Δ': u'D', u'Ε': u'E', u'Ζ': u'Z', u'Η': u'H', u'Θ': u'8',
    u'Ι': u'I', u'Κ': u'K', u'Λ': u'L', u'Μ': u'M', u'Ν': u'N', u'Ξ': u'3', u'Ο': u'O', u'Π': u'P',
    u'Ρ': u'R', u'Σ': u'S', u'Τ': u'T', u'Υ': u'Y', u'Φ': u'F', u'Χ': u'X', u'Ψ': u'PS', u'Ω': u'W',
    u'Ά': u'A', u'Έ': u'E', u'Ί': u'I', u'Ό': u'O', u'Ύ': u'Y', u'Ή': u'H', u'Ώ': u'W', u'Ϊ': u'I',
    u'Ϋ': u'Y'
}

turkish_map = {
    u'ş': u's', u'Ş': u'S', u'ı': u'i', u'İ': u'I', u'ç': u'c', u'Ç': u'C', u'ü': u'u', u'Ü': u'U',
    u'ö': u'o', u'Ö': u'O', u'ğ': u'g', u'Ğ': u'G'
}

russian_map = {
    u'а': u'a', u'б': u'b', u'в': u'v', u'г': u'g', u'д': u'd', u'е': u'e', u'ё': u'yo', u'ж': u'zh',
    u'з': u'z', u'и': u'i', u'й': u'j', u'к': u'k', u'л': u'l', u'м': u'm', u'н': u'n', u'о': u'o',
    u'п': u'p', u'р': u'r', u'с': u's', u'т': u't', u'у': u'u', u'ф': u'f', u'х': u'h', u'ц': u'c',
    u'ч': u'ch', u'ш': u'sh', u'щ': u'sh', u'ъ': u'', u'ы': u'y', u'ь': u'', u'э': u'e', u'ю': u'yu',
    u'я': u'ya',
    u'А': u'A', u'Б': u'B', u'В': u'V', u'Г': u'G', u'Д': u'D', u'Е': u'E', u'Ё': u'Yo', u'Ж': u'Zh',
    u'З': u'Z', u'И': u'I', u'Й': u'J', u'К': u'K', u'Л': u'L', u'М': u'M', u'Н': u'N', u'О': u'O',
    u'П': u'P', u'Р': u'R', u'С': u'S', u'Т': u'T', u'У': u'U', u'Ф': u'F', u'Х': u'H', u'Ц': u'C',
    u'Ч': u'Ch', u'Ш': u'Sh', u'Щ': u'Sh', u'Ъ': u'', u'Ы': u'Y', u'Ь': u'', u'Э': u'E', u'Ю': u'Yu',
    u'Я': u'Ya'
}

ukrainian_map = {
    u'Є': u'Ye', u'І': u'I', u'Ї': u'Yi', u'Ґ': u'G', u'є': u'ye', u'і': u'i', u'ї': u'yi', u'ґ': u'g'
}

czech_map = {
    u'č': u'c', u'ď': u'd', u'ě': u'e', u'ň': u'n', u'ř': u'r', u'š': u's', u'ť': u't', u'ů': u'u',
    u'ž': u'z', u'Č': u'C', u'Ď': u'D', u'Ě': u'E', u'Ň': u'N', u'Ř': u'R', u'Š': u'S', u'Ť': u'T',
    u'Ů': u'U', u'Ž': u'Z'
}

polish_map = {
    u'ą': u'a', u'ć': u'c', u'ę': u'e', u'ł': u'l', u'ń': u'n', u'ó': u'o', u'ś': u's', u'ź': u'z',
    u'ż': u'z', u'Ą': u'A', u'Ć': u'C', u'Ę': u'e', u'Ł': u'L', u'Ń': u'N', u'Ó': u'o', u'Ś': u'S',
    u'Ź': u'Z', u'Ż': u'Z'
}

latvian_map = {
    u'ā': u'a', u'č': u'c', u'ē': u'e', u'ģ': u'g', u'ī': u'i', u'ķ': u'k', u'ļ': u'l', u'ņ': u'n',
    u'š': u's', u'ū': u'u', u'ž': u'z', u'Ā': u'A', u'Č': u'C', u'Ē': u'E', u'Ģ': u'G', u'Ī': u'i',
    u'Ķ': u'k', u'Ļ': u'L', u'Ņ': u'N', u'Š': u'S', u'Ū': u'u', u'Ž': u'Z'
}
