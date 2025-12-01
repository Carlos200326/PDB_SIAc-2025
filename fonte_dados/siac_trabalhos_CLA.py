import pdfplumber
import re
import pandas as pd

PDF_PATH = "SIAC_CLA_Caderno_Resumo.pdf"   # coloque o PDF na mesma pasta do script
OUTPUT_CSV = "siac_cla_trabalhos.csv"

# Regex para captura dos campos
REG_AREA = r"ÁREA PRINCIPAL:\s*(.+)"
REG_MODAL = r"MODALIDADE DE APRESENTAÇÃO:\s*(.+)"
REG_ARTIGO = r"ARTIGO:\s*(\d+)"
REG_TITULO = r"TITULO[: ]\s*(.+)"
REG_AUTOR = r"AUTOR\(ES\):\s*(.+)"
REG_ORIENT = r"ORIENTADOR\(ES\):\s*(.+)"


def extract_block(text):
    """Extrai todos os campos de um bloco de texto contendo um trabalho."""
    area = re.search(REG_AREA, text)
    mod = re.search(REG_MODAL, text)
    art = re.search(REG_ARTIGO, text)
    tit = re.search(REG_TITULO, text)
    aut = re.search(REG_AUTOR, text)
    ori = re.search(REG_ORIENT, text)

    # Resumo: entre RESUMO e BIBLIOGRAFIA
    resumo_match = re.search(r"RESUMO:\s*(.+?)(BIBLIOGRAFIA:)", text, flags=re.S)

    if resumo_match:
        resumo = resumo_match.group(1).strip()
        bib_match = re.search(r"BIBLIOGRAFIA:\s*(.+)", text, flags=re.S)
        bibliografia = bib_match.group(1).strip() if bib_match else ""
    else:
        resumo = ""
        bibliografia = ""

    return {
        "area": area.group(1).strip() if area else "",
        "modalidade": mod.group(1).strip() if mod else "",
        "artigo": art.group(1).strip() if art else "",
        "titulo": tit.group(1).strip() if tit else "",
        "autores": aut.group(1).strip() if aut else "",
        "orientadores": ori.group(1).strip() if ori else "",
        "resumo": resumo,
        "bibliografia": bibliografia
    }


def extract_pdf(pdf_path):
    registros = []
    fulltext = ""

    print("\nLendo PDF página por página...\n")

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Processando página {i+1}/{len(pdf.pages)}...")
            txt = page.extract_text()
            if txt:
                fulltext += "\n" + txt

    print("\nSeparando trabalhos...\n")

    # Cada trabalho começa com "ÁREA PRINCIPAL:"
    blocos = re.split(r"ÁREA PRINCIPAL:\s*", fulltext)

    for bloco in blocos[1:]:  # Ignora primeira parte sem conteúdo
        bloco = "ÁREA PRINCIPAL: " + bloco  
        dados = extract_block(bloco)
        registros.append(dados)

    return registros


# -------------- EXECUÇÃO PRINCIPAL --------------------

registros = extract_pdf(PDF_PATH)

df = pd.DataFrame(registros)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("\nExtração concluída!")
print(f"Arquivo salvo como: {OUTPUT_CSV}")
print(df.head())
