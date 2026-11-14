#!/usr/bin/env python3
"""Genera las tarjetas SVG del perfil en assets/ (modo claro y oscuro) con la estética
terminal del banner: open-source, certifications y hackathons.

Cada tarjeta lee su lista de un JSON en tools/. Un item puede usar el esquema original
(project, repo, issue o ref, kind, summary, verified, shipped, detail) o el esquema
genérico (tag, pill, project opcional, summary, detail)."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).parent
OUT = HERE.parent / "assets"
W = 960
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(page="#0e1116", bar="#161b24", body="#12161d", border="#2a313c",
                 text="#e6eaf0", muted="#7d8794", accent="#7dd3c0", warm="#e9b872"),
    "light": dict(page="#f4f0e7", bar="#f1eee6", body="#fbf9f4", border="#d8d2c4",
                  text="#241e14", muted="#7a7466", accent="#0f766e", warm="#b45309"),
}

CARDS = [
    dict(slug="open-source", json="contributions.json", title="Open source contributions",
         window="open-source — zsh", cmd="open-source --list"),
    dict(slug="certifications", json="certifications.json", title="Certifications",
         window="certifications — zsh", cmd="certs --list"),
    dict(slug="hackathons", json="hackathons.json", title="Hackathons",
         window="hackathons — zsh", cmd="hackathons --list"),
]


def normalize(it):
    """Lleva un item del esquema original al genérico (tag, pill, project, summary, detail)."""
    if "tag" in it:
        return it
    ref = it.get("ref", it.get("issue"))
    bits = []
    if it.get("detail"):
        bits.append(it["detail"])
    else:
        if it.get("verified"):
            bits.append("fix verified")
        if it.get("shipped"):
            bits.append("shipped " + ", ".join(it["shipped"]))
    return dict(tag=f"#{ref}", pill=it["kind"], project=it.get("project"),
                summary=it["summary"], detail=" · ".join(bits))


def build(theme, card, items):
    c = THEMES[theme]
    items = [normalize(i) for i in items]
    top, row_h = 44, 64
    head = top + 52
    H = head + len(items) * row_h + 84
    esc = escape
    o = []
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">')
    o.append(f'<title id="t">{esc(card["title"])}</title>')
    desc = "; ".join(
        (f'{i["project"]} ' if i.get("project") else "")
        + f'{i["tag"]} {i["pill"]}: {i["summary"]}'
        + (f' ({i["detail"]})' if i.get("detail") else "")
        for i in items)
    o.append(f'<desc id="d">{esc(desc)}</desc>')
    o.append(f'<defs><filter id="sh" x="-5%" y="-10%" width="110%" height="130%"><feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity=".22"/></filter>'
             f'<clipPath id="win"><rect x="24" y="12" width="{W-48}" height="{H-36}" rx="10"/></clipPath></defs>')
    o.append(f'<g filter="url(#sh)"><rect x="24" y="12" width="{W-48}" height="{H-36}" rx="10" fill="{c["body"]}" stroke="{c["border"]}"/></g>')
    o.append(f'<g clip-path="url(#win)"><rect x="24" y="12" width="{W-48}" height="{top}" fill="{c["bar"]}"/>'
             f'<line x1="24" y1="{12+top}" x2="{W-24}" y2="{12+top}" stroke="{c["border"]}"/></g>')
    for k, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        o.append(f'<circle cx="{50+k*22}" cy="{12+top/2}" r="6" fill="{col}"/>')
    o.append(f'<text x="{W/2}" y="{12+top/2+5}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{c["muted"]}">{esc(card["window"])}</text>')

    def fade(begin):
        return f'<animate attributeName="opacity" from="0" to="1" dur=".5s" begin="{begin:.2f}s" fill="freeze"/>'

    y0 = 12 + top + 40
    o.append(f'<g opacity="0">{fade(0.2)}<text x="56" y="{y0}" font-family="{FONT}" font-size="16" fill="{c["accent"]}">❯</text>'
             f'<text x="80" y="{y0}" font-family="{FONT}" font-size="16" fill="{c["text"]}">{esc(card["cmd"])}</text></g>')
    for n, it in enumerate(items):
        y = y0 + 38 + n * row_h
        b = 0.7 + n * 0.45
        o.append(f'<g opacity="0">{fade(b)}')
        o.append(f'<text x="56" y="{y}" font-family="{FONT}" font-size="16" font-weight="700" fill="{c["accent"]}">{esc(it["tag"])}</text>')
        o.append(f'<rect x="124" y="{y-16}" width="104" height="24" rx="12" fill="none" stroke="{c["border"]}"/>')
        o.append(f'<text x="176" y="{y}" text-anchor="middle" font-family="{FONT}" font-size="14" fill="{c["warm"]}">{esc(it["pill"])}</text>')
        sx = 248
        if it.get("project"):
            o.append(f'<text x="248" y="{y}" font-family="{FONT}" font-size="16" font-weight="700" fill="{c["text"]}">{esc(it["project"])}</text>')
            sx = 352
        o.append(f'<text x="{sx}" y="{y}" font-family="{FONT}" font-size="16" fill="{c["text"]}">{esc(it["summary"])}</text>')
        if it.get("detail"):
            o.append(f'<text x="124" y="{y+26}" font-family="{FONT}" font-size="14" fill="{c["muted"]}">↳ {esc(it["detail"])}</text>')
        o.append('</g>')
    yl = y0 + 38 + len(items) * row_h
    t0 = 0.7 + len(items) * 0.45
    o.append(f'<g opacity="0">{fade(t0)}<text x="56" y="{yl}" font-family="{FONT}" font-size="16" fill="{c["accent"]}">❯</text></g>')
    o.append(f'<rect x="80" y="{yl-13}" width="9" height="18" fill="{c["accent"]}" opacity="0">'
             f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.01;.5;.51;1" dur="1.2s" begin="{t0:.2f}s" repeatCount="indefinite"/></rect>')
    o.append('</svg>')
    return "".join(o)


def main():
    OUT.mkdir(exist_ok=True)
    for card in CARDS:
        src = HERE / card["json"]
        if not src.exists():
            continue
        items = json.loads(src.read_text(encoding="utf-8"))
        for theme in THEMES:
            p = OUT / f'{card["slug"]}-{theme}.svg'
            p.write_text(build(theme, card, items), encoding="utf-8")
            print("escrito", p, p.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
