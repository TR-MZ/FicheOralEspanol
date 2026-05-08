#!/usr/bin/env python3
import os
import zipfile
from datetime import datetime
from html import escape


OUT = "/Users/xavierjara/Downloads/ImagesEspaniol/fiche_image_2_ficciones_mundo_mejor.docx"


def tx(text):
    return escape(text, quote=False)


def p(text="", style=None, bold=False, italic=False, size=None, color=None, after=None, before=None):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if before is not None or after is not None:
        attrs = []
        if before is not None:
            attrs.append(f'w:before="{before}"')
        if after is not None:
            attrs.append(f'w:after="{after}"')
        ppr.append(f'<w:spacing {" ".join(attrs)} w:line="276" w:lineRule="auto"/>')
    rpr = []
    if bold:
        rpr.append("<w:b/>")
    if italic:
        rpr.append("<w:i/>")
    if size:
        rpr.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    if color:
        rpr.append(f'<w:color w:val="{color}"/>')
    return (
        "<w:p>"
        + (f"<w:pPr>{''.join(ppr)}</w:pPr>" if ppr else "")
        + "<w:r>"
        + (f"<w:rPr>{''.join(rpr)}</w:rPr>" if rpr else "")
        + f"<w:t>{tx(text)}</w:t>"
        + "</w:r></w:p>"
    )


def bullet_item(text):
    return (
        '<w:p><w:pPr><w:pStyle w:val="ListParagraph"/>'
        '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
        '<w:spacing w:after="80" w:line="276" w:lineRule="auto"/></w:pPr>'
        f'<w:r><w:t>{tx(text)}</w:t></w:r></w:p>'
    )


def cell(content, width, fill=None, bold=False, grid_span=None):
    shading = f'<w:shd w:fill="{fill}"/>' if fill else ""
    span = f'<w:gridSpan w:val="{grid_span}"/>' if grid_span else ""
    tcpr = (
        f'<w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>{span}'
        '<w:tcMar><w:top w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/>'
        '<w:start w:w="160" w:type="dxa"/><w:end w:w="160" w:type="dxa"/></w:tcMar>'
        f"{shading}<w:vAlign w:val=\"center\"/></w:tcPr>"
    )
    if isinstance(content, list):
        body = "".join(bullet_item(item) for item in content)
    else:
        body = p(content, bold=bold, after=40)
    return f"<w:tc>{tcpr}{body}</w:tc>"


def row(cells, cant_split=True):
    trpr = "<w:trPr><w:cantSplit/></w:trPr>" if cant_split else ""
    return f"<w:tr>{trpr}{''.join(cells)}</w:tr>"


def axis_table(axis_title, vocab, grammar, docs):
    full = 9360
    left = 3550
    right = full - left
    rows = [
        row([cell(axis_title, full, fill="F1F3F4", bold=True, grid_span=2)]),
        row([
            cell("Vocabulaire essentiel", left, fill="F8F9FA", bold=True),
            cell("Temps et formes grammaticales", right, fill="F8F9FA", bold=True),
        ]),
        row([cell(vocab, left), cell(grammar, right)]),
        row([
            cell("Document / support", left, fill="F8F9FA", bold=True),
            cell("Aspects de l’axe traités", right, fill="F8F9FA", bold=True),
        ]),
    ]
    for support, aspects in docs:
        rows.append(row([cell(support, left, bold=True), cell(aspects, right)]))
    return (
        '<w:tbl><w:tblPr><w:tblStyle w:val="TableGrid"/>'
        '<w:tblW w:w="9360" w:type="dxa"/><w:tblLayout w:type="fixed"/>'
        '<w:tblBorders><w:top w:val="single" w:sz="6" w:color="DADCE0"/>'
        '<w:left w:val="single" w:sz="6" w:color="DADCE0"/>'
        '<w:bottom w:val="single" w:sz="6" w:color="DADCE0"/>'
        '<w:right w:val="single" w:sz="6" w:color="DADCE0"/>'
        '<w:insideH w:val="single" w:sz="6" w:color="DADCE0"/>'
        '<w:insideV w:val="single" w:sz="6" w:color="DADCE0"/></w:tblBorders>'
        '<w:tblCellMar><w:top w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/>'
        '<w:start w:w="160" w:type="dxa"/><w:end w:w="160" w:type="dxa"/></w:tblCellMar>'
        '</w:tblPr><w:tblGrid><w:gridCol w:w="3550"/><w:gridCol w:w="5810"/></w:tblGrid>'
        + "".join(rows)
        + "</w:tbl>"
    )


def styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/><w:szCs w:val="22"/><w:color w:val="000000"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="160" w:line="276" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="22"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="200" w:line="276" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:b/><w:sz w:val="48"/><w:color w:val="000000"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:spacing w:after="280" w:line="276" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="24"/><w:color w:val="555555"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:pPr><w:ind w:left="720"/><w:spacing w:after="80" w:line="276" w:lineRule="auto"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/><w:sz w:val="21"/></w:rPr></w:style>
  <w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="59"/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="120" w:type="dxa"/><w:bottom w:w="120" w:type="dxa"/><w:start w:w="160" w:type="dxa"/><w:end w:w="160" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
</w:styles>"""


def numbering_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:multiLevelType w:val="hybridMultilevel"/>
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs><w:ind w:left="720" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:hint="default"/></w:rPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""


def document_xml():
    body = [
        p("Fiche de révision - Image 2", style="Title"),
        p("Suite de Ficciones y realidad, puis Mundo mejor", style="Subtitle"),
        axis_table(
            "3. Ficciones y realidad (+ territorio y memoria)",
            [
                "ficción / realidad",
                "la mirada, el punto de vista",
                "la memoria, el territorio",
                "la violencia machista",
                "la denuncia, la justicia",
                "la igualdad / la desigualdad",
            ],
            [
                "pretérito indefinido e imperfecto para relatar y contextualizar",
                "presente para describir y comentar",
                "conectores: porque, sin embargo, por eso, aunque",
                "expresar obligación o necesidad: hay que, tener que, deber",
            ],
            [
                (
                    "la serie: La otra mirada (fragmento con Roberta)",
                    "Relación entre ficción y realidad; representación de una sociedad y de la condición de las mujeres; memoria de un territorio o de una época; mirada crítica.",
                ),
                (
                    "Pamplona (2016): violencia machista",
                    "Hecho real vinculado a la violencia machista; denuncia social; justicia, memoria colectiva y evolución de las mentalidades.",
                ),
            ],
        ),
        p("", after=220),
        axis_table(
            "4. Mundo mejor: ¿para todos? ¿A corto/largo plazo? > Innovaciones científicas y responsabilidad + territorio y memoria",
            [
                "un invento, innovar",
                "ventajas e inconvenientes",
                "la responsabilidad",
                "el cambio climático, la sequía",
                "el agua, los ríos, el desvío",
                "las redes sociales, los menores",
            ],
            [
                "futuro y condicional para imaginar consecuencias",
                "hipótesis: si + presente / futuro",
                "comparativos y expresiones de opinión",
                "obligación, prohibición y consejo: hay que, no se debe, está prohibido",
                "para + infinitivo para expresar finalidad",
            ],
            [
                (
                    "inventos",
                    "Ventajas e inconvenientes de la innovación; progreso científico y responsabilidad ante sus efectos.",
                ),
                (
                    "balance climático de AEMET + desafío del agua + predicciones",
                    "Cambio climático, gestión del agua y necesidad de prever riesgos a corto y largo plazo.",
                ),
                (
                    "los ríos de España: desvío del río Tajo",
                    "Territorio, recursos hídricos y tensiones entre necesidades locales, memoria del paisaje y decisiones colectivas.",
                ),
                (
                    "máquinas Atecfrío",
                    "Uso de la tecnología para responder a necesidades concretas; innovación práctica y responsabilidad en sus aplicaciones.",
                ),
                (
                    "prohibición de redes sociales para menores de 16 años",
                    "Debate sobre protección, libertad y responsabilidad digital; impacto de la tecnología en los jóvenes.",
                ),
            ],
        ),
    ]
    sect = (
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="708" w:footer="708" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="360"/></w:sectPr>'
    )
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
        'mc:Ignorable="w14 wp14"><w:body>'
        + "".join(body)
        + sect
        + "</w:body></w:document>"
    )


def write_docx(path):
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    files = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>""",
        "word/document.xml": document_xml(),
        "word/styles.xml": styles_xml(),
        "word/numbering.xml": numbering_xml(),
        "word/settings.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/><w:proofState w:spelling="clean" w:grammar="clean"/></w:settings>""",
        "docProps/core.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Fiche de révision - Image 2</dc:title>
  <dc:creator>Codex</dc:creator>
  <cp:lastModifiedBy>Codex</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>""",
        "docProps/app.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"><Application>Codex</Application></Properties>""",
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


if __name__ == "__main__":
    write_docx(OUT)
    print(OUT)
