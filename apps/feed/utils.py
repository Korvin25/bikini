# -*- coding: utf-8 -*-
from functools import reduce 


def html_unescape(text):
    html_escape_table = [
        ['&amp;', "&amp;amp;"],
        ['"', "&amp;quot;"],
        ["'", "&amp;apos;"],
        [">", "&amp;gt;"],
        ["<", "&amp;lt;"],
        [" ", "&amp;nbsp;"],
        ["«", "&amp;laquo;"],
        ["»", "&amp;raquo;"],
        ["–", "&amp;ndash;"],
        ["—", "&amp;mdash;"],
        ["Š", "&amp;Scaron;"],
        ['"', "&quot;"],
        ["'", "&apos;"],
        [">", "&gt;"],
        ["<", "&lt;"],
        [" ", "&nbsp;"],
        ["«", "&laquo;"],
        ["»", "&raquo;"],
        ["–", "&ndash;"],
        ["—", "&mdash;"],
        ["Š", "&Scaron;"],
    ]
    return reduce(lambda text, x: text.replace(x[1], x[0]), html_escape_table, text)
