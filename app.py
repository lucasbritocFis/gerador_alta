import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import fitz  # PyMuPDF
import io
import numpy as np

def cortar_ate_texto(imagem):
    dpi = 300
    cm_para_cortar = 4
    polegadas_para_cortar = cm_para_cortar / 2.54
    pixels_para_cortar = int(polegadas_para_cortar * dpi)
    largura, altura = imagem.size
    img_cortada_inicial = imagem.crop((0, pixels_para_cortar, largura, altura))
    img_array = np.array(img_cortada_inicial.convert("L"))
    nova_altura, nova_largura = img_array.shape
    limiar_branco = 245
    ultima_linha = 0
    for y in range(nova_altura):
        if np.mean(img_array[y, :]) < limiar_branco:
            ultima_linha = y
    margem = 20
    bottom = min(ultima_linha + margem, nova_altura)
    img_cortada_final = img_cortada_inicial.crop((0, 0, nova_largura, bottom))
    return img_cortada_final


st.title("Gerador de Relatório com Página 2 Customizada")

uploaded_pdf_modelo = st.file_uploader("PDF RELATÓRIO FÍSICA", type="pdf")
uploaded_pdf_alta = st.file_uploader("PDF RELATÓRIO ALTA MÉDICA", type="pdf")

x = st.number_input("Posição X da imagem", value=34)
y = st.number_input("Posição Y da imagem", value=28)
width = st.number_input("Largura da imagem", value=540)
height = st.number_input("Altura da imagem", value=620)

if uploaded_pdf_modelo and uploaded_pdf_alta:
    modelo = PdfReader(uploaded_pdf_modelo)

    alta_bytes = uploaded_pdf_alta.read()
    doc = fitz.open(stream=alta_bytes, filetype="pdf")
    
    # Extrair texto da primeira página para nome e ID
    texto_pagina = doc.load_page(0).get_text("text")
    linhas = texto_pagina.strip().splitlines()
    nome_paciente = linhas[0].strip()
    prontuario = ""
    for linha in linhas:
        if "ID:" in linha:
            prontuario = linha.split("ID:")[1].strip()
            break

    # Nome do arquivo de saída
    output_alta = f"ALTA - {nome_paciente} (ID {prontuario}).pdf"

    # Converter página em imagem
    pix = doc.load_page(0).get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img_cortada = cortar_ate_texto(img)

    # Usar ImageReader do ReportLab
    image_reader = ImageReader(img_cortada)

    # Criar camada de imagem
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.drawImage(image_reader, x, y, width=width, height=height)
    c.save()
    packet.seek(0)

    # Inserir imagem na página 2 do modelo
    overlay_pdf = PdfReader(packet)
    pagina2 = modelo.pages[1]
    pagina2.merge_page(overlay_pdf.pages[0])

    # Gerar PDF final
    output = PdfWriter()
    output.add_page(modelo.pages[0])
    output.add_page(pagina2)
    for page in modelo.pages[2:]:
        output.add_page(page)

    final_buffer = io.BytesIO()
    output.write(final_buffer)

    # Botão de download
    st.download_button("📄 Baixar PDF final", data=final_buffer.getvalue(), file_name=output_alta)
