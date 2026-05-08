from __future__ import annotations

import html
import os
import zipfile
from pathlib import Path


OUT = Path("/Users/xavierjara/Downloads/ImagesEspaniol/fiche_image_1_langues_famille.docx")


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def r_text(text: str, bold: bool = False, italic: bool = False, color: str | None = None, size: int | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if color:
        props.append(f'<w:color w:val="{color}"/>')
    if size:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    space = ' xml:space="preserve"' if text.startswith(" ") or text.endswith(" ") else ""
    return f"<w:r>{rpr}<w:t{space}>{esc(text)}</w:t></w:r>"


def para(
    text: str = "",
    style: str | None = None,
    *,
    bold: bool = False,
    italic: bool = False,
    color: str | None = None,
    size: int | None = None,
    before: int | None = None,
    after: int | None = None,
    keep_next: bool = False,
) -> str:
    style_xml = f'<w:pStyle w:val="{style}"/>' if style else ""
    spacing = ""
    if before is not None or after is not None:
        before_attr = f' w:before="{before}"' if before is not None else ""
        after_attr = f' w:after="{after}"' if after is not None else ""
        spacing = f"<w:spacing{before_attr}{after_attr} w:line=\"276\" w:lineRule=\"auto\"/>"
    keep = "<w:keepNext/>" if keep_next else ""
    ppr = f"<w:pPr>{style_xml}{keep}{spacing}</w:pPr>" if style_xml or spacing or keep else ""
    return f"<w:p>{ppr}{r_text(text, bold=bold, italic=italic, color=color, size=size)}</w:p>"


def cell(paragraphs: list[str], width: int, *, fill: str | None = None, grid_span: int | None = None) -> str:
    span = f'<w:gridSpan w:val="{grid_span}"/>' if grid_span else ""
    fill_xml = f'<w:shd w:fill="{fill}"/>' if fill else ""
    tcpr = (
        f"<w:tcPr><w:tcW w:w=\"{width}\" w:type=\"dxa\"/>"
        f"{span}{fill_xml}"
        "<w:tcMar>"
        '<w:top w:w="100" w:type="dxa"/>'
        '<w:start w:w="140" w:type="dxa"/>'
        '<w:bottom w:w="100" w:type="dxa"/>'
        '<w:end w:w="140" w:type="dxa"/>'
        "</w:tcMar>"
        "<w:vAlign w:val=\"center\"/>"
        "</w:tcPr>"
    )
    return f"<w:tc>{tcpr}{''.join(paragraphs)}</w:tc>"


def row(cells: list[str], cant_split: bool = True) -> str:
    trpr = "<w:trPr><w:cantSplit/></w:trPr>" if cant_split else ""
    return f"<w:tr>{trpr}{''.join(cells)}</w:tr>"


def table(axis_title: str, vocab: str, grammar: str, documents: list[tuple[str, str]]) -> str:
    left = 3500
    right = 5860
    width = left + right
    borders = (
        "<w:tblBorders>"
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        '<w:insideH w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        '<w:insideV w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/>'
        "</w:tblBorders>"
    )
    parts = [
        "<w:tbl>",
        "<w:tblPr>",
        '<w:tblStyle w:val="TableGrid"/>',
        '<w:tblW w:w="9360" w:type="dxa"/>',
        '<w:tblInd w:w="0" w:type="dxa"/>',
        "<w:tblLayout w:type=\"fixed\"/>",
        borders,
        "<w:tblCellMar>"
        '<w:top w:w="100" w:type="dxa"/>'
        '<w:start w:w="140" w:type="dxa"/>'
        '<w:bottom w:w="100" w:type="dxa"/>'
        '<w:end w:w="140" w:type="dxa"/>'
        "</w:tblCellMar>",
        "</w:tblPr>",
        f"<w:tblGrid><w:gridCol w:w=\"{left}\"/><w:gridCol w:w=\"{right}\"/></w:tblGrid>",
        row([cell([para(axis_title, bold=True, size=24, keep_next=True)], width, fill="F8F9FA", grid_span=2)]),
        row(
            [
                cell([para("Vocabulaire essentiel", bold=True)], left, fill="F8F9FA"),
                cell([para("Temps et formes grammaticales", bold=True)], right, fill="F8F9FA"),
            ]
        ),
        row([cell([para(vocab)], left), cell([para(grammar)], right)]),
        row(
            [
                cell([para("Document / support", bold=True)], left, fill="F8F9FA"),
                cell([para("Aspects de l’axe traités", bold=True)], right, fill="F8F9FA"),
            ]
        ),
    ]
    for support, aspects in documents:
        parts.append(row([cell([para(support)], left), cell([para(aspects)], right)]))
    parts.append("</w:tbl>")
    parts.append(para("", after=120))
    return "".join(parts)


def document_xml() -> str:
    lang_docs = [
        (
            "Énigme : palabra « agur »",
            "Una palabra como pista de identidad, contacto lingüístico y memoria de un territorio.",
        ),
        (
            "Caricatura de Pedro Sánchez y lenguas cooficiales en el Congreso español",
            "Debate sobre la presencia pública de las lenguas cooficiales y su papel en la vida política.",
        ),
        (
            "Citas sobre las lenguas, por ejemplo Carlomagno",
            "Reflexión sobre aprender idiomas, entender otras culturas y construir una identidad abierta.",
        ),
    ]
    familia_docs = [
        (
            "El NO-DO",
            "Representación pública de modelos familiares y sociales en un contexto histórico oficial.",
        ),
        (
            "Los yanomamis y los wayuus, tribus indígenas",
            "Diversidad de estructuras familiares, transmisión cultural y relación entre comunidad e identidad.",
        ),
        (
            "Medidas de conciliación de la vida laboral y familiar por los hombres",
            "Reparto de responsabilidades, igualdad y evolución del papel de los hombres en la esfera privada.",
        ),
        (
            "Ley de familia: permisos, regulación del papel, reconocimiento, ayuda económica...",
            "Reconocimiento institucional de diferentes situaciones familiares y apoyo a la vida familiar.",
        ),
        (
            "Reportaje sobre el permiso de paternidad",
            "Paternidad, conciliación, corresponsabilidad y cambios en las relaciones privado / público.",
        ),
    ]
    fiction_docs = [
        (
            "Début de l’axe visible sur la capture",
            "Note : l’axe continue sur l’image suivante ; seuls le titre et l’association avec territorio y memoria sont visibles ici.",
        )
    ]

    body = [
        para("Fiche de révision - Image 1", style="Title"),
        para(
            "Axes visibles sur la capture : Langues, Familia, début de Ficciones y realidad",
            style="Subtitle",
        ),
        para(
            "Tableaux de révision construits à partir des éléments visibles sur la capture. Les formulations restent synthétiques lorsque le détail des documents n’est pas entièrement lisible.",
            style="Normal",
            after=160,
        ),
        table(
            "Langues > identidades e intercambios + territorio y memoria",
            "lenguas cooficiales ; identidad lingüística ; intercambio cultural ; memoria ; territorio ; Congreso ; cita ; agur",
            "Presente de indicativo para presentar documentos ; verbos de opinión ; conectores para explicar una relación ; comparación sencilla.",
            lang_docs,
        ),
        table(
            "Familia > privado / público",
            "familia ; vida laboral ; vida familiar ; conciliación ; permiso de paternidad ; reconocimiento ; ayuda económica ; pueblos indígenas ; corresponsabilidad",
            "Presente para describir medidas y documentos ; pasado para situar el NO-DO ; obligación y necesidad : tener que, deber, hay que ; comparación entre modelos familiares.",
            familia_docs,
        ),
        table(
            "Ficciones y realidad (+ territorio y memoria)",
            "ficción ; realidad ; memoria ; territorio ; representación",
            "Formes à compléter avec les documents de l’image suivante.",
            fiction_docs,
        ),
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
        'xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" '
        'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
        'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
        'mc:Ignorable="w14 wp14">'
        "<w:body>"
        + "".join(body)
        + '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
        "</w:body></w:document>"
    )


def styles_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="000000"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="000000"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:before="0" w:after="200" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:b/><w:sz w:val="48"/><w:szCs w:val="48"/><w:color w:val="000000"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle">
    <w:name w:val="Subtitle"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:spacing w:after="240" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="24"/><w:szCs w:val="24"/><w:color w:val="555555"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:keepNext/><w:spacing w:before="360" w:after="160" w:line="276" w:lineRule="auto"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/><w:color w:val="000000"/></w:rPr>
  </w:style>
  <w:style w:type="table" w:styleId="TableGrid">
    <w:name w:val="Table Grid"/>
    <w:basedOn w:val="TableNormal"/>
    <w:uiPriority w:val="39"/>
    <w:tblPr><w:tblBorders><w:top w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/><w:left w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/><w:right w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/><w:insideH w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/><w:insideV w:val="single" w:sz="6" w:space="0" w:color="DADCE0"/></w:tblBorders></w:tblPr>
  </w:style>
  <w:style w:type="table" w:default="1" w:styleId="TableNormal">
    <w:name w:val="Normal Table"/>
    <w:semiHidden/>
    <w:uiPriority w:val="99"/>
    <w:unhideWhenUsed/>
    <w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="80" w:type="dxa"/><w:start w:w="120" w:type="dxa"/><w:bottom w:w="80" w:type="dxa"/><w:end w:w="120" w:type="dxa"/></w:tblCellMar></w:tblPr>
  </w:style>
</w:styles>
"""


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>
"""

SETTINGS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="720"/>
  <w:compat/>
</w:settings>
"""

CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Fiche de révision - Image 1</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">2026-05-08T00:00:00Z</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">2026-05-08T00:00:00Z</dcterms:modified>
</cp:coreProperties>
"""

APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        raise FileExistsError(f"Refusing to overwrite existing file: {OUT}")
    tmp = OUT.with_suffix(".tmp.docx")
    files = {
        "[Content_Types].xml": CONTENT_TYPES,
        "_rels/.rels": RELS,
        "word/_rels/document.xml.rels": DOC_RELS,
        "word/document.xml": document_xml(),
        "word/styles.xml": styles_xml(),
        "word/settings.xml": SETTINGS,
        "docProps/core.xml": CORE,
        "docProps/app.xml": APP,
    }
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    os.replace(tmp, OUT)
    print(OUT)


if __name__ == "__main__":
    main()
