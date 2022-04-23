"""
XML utils
"""
import htmlentitydefs
import re


def delete_byte_codes(string):
    """
    Remove byte codes (\\x00, \\x01, ..., \\x1f) from string and return result string.
    Need remove this codes for correct parsing XML (for example)
    """

    byte_codes = [
        u'\x00', u'\x01', u'\x02', u'\x03', u'\x04', u'\x05', u'\x06', u'\x07', u'\x08', u'\x09',
        u'\x0a', u'\x0b', u'\x0c', u'\x0d', u'\x0e', u'\x0f',
        u'\x10', u'\x11', u'\x12', u'\x13', u'\x14', u'\x15', u'\x16', u'\x17', u'\x18', u'\x19',
        u'\x1a', u'\x1b', u'\x1c', u'\x1d', u'\x1e', u'\x1f']
    res_str = string
    for char in byte_codes:
        res_str = res_str.replace(char, '')

    return res_str


def unescape(text):
    """
    Removes HTML or XML character references
      and entities from a text string.
    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.
    from Fredrik Lundh
    2008-01-03: input only unicode characters string.
    http://effbot.org/zone/re-sub.htm#unescape-html
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                print("Value Error")
                pass
        else:
            # named entity
            # reescape the reserved characters.
            try:
                if text[1:-1] == "amp":
                    text = "&amp;amp;"
                elif text[1:-1] == "gt":
                    text = "&amp;gt;"
                elif text[1:-1] == "lt":
                    text = "&amp;lt;"
                else:
                    print(text[1:-1])
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                print("keyerror")
                pass
        return text  # leave as is

    return re.sub("&#?\w+;", fixup, text)
