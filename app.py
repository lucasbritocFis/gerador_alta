import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import fitz  # PyMuPDF
import io
import numpy as np
import base64
import streamlit.components.v1 as components
import os
def cortar_ate_texto(imagem):
    dpi = 300
    cm_para_cortar = 3
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



st.set_page_config(layout="wide")
st.title("ANEXAR RELATÓRIO DE ALTA PARA O RELATÓRIO DE ALTA MÉDICA")

col1, col2 = st.columns(2)

with col1:
    uploaded_pdf_modelo = st.file_uploader("PDF RELATÓRIO FÍSICA", type="pdf")
    uploaded_pdf_alta = st.file_uploader("PDF RELATÓRIO ALTA MÉDICA", type="pdf")

with col2:
    col_x, col_y = st.columns(2)
    with col_x:
        x = st.number_input("Posição X", value=34)
        width = st.number_input("Largura", value=540)
    with col_y:
        y = st.number_input("Posição Y", value=28)
        height = st.number_input("Altura", value=620)

if uploaded_pdf_modelo and uploaded_pdf_alta:
    try:
        # Nome do arquivo de saída baseado no nome do modelo
        nome_base = os.path.splitext(uploaded_pdf_modelo.name)[0]
        output_alta = f"{nome_base}.pdf"

        modelo = PdfReader(uploaded_pdf_modelo)
        alta_bytes = uploaded_pdf_alta.read()
        doc = fitz.open(stream=alta_bytes, filetype="pdf")

        # Converter primeira página do PDF de alta em imagem
        pix = doc.load_page(0).get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        img_cortada = cortar_ate_texto(img)

        # Criar sobreposição com imagem cortada
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.drawImage(ImageReader(img_cortada), x, y, width=width, height=height)
        c.save()
        packet.seek(0)

        overlay_pdf = PdfReader(packet)
        pagina2 = modelo.pages[1]
        pagina2.merge_page(overlay_pdf.pages[0])

        output = PdfWriter()
        output.add_page(modelo.pages[0])
        output.add_page(pagina2)
        for page in modelo.pages[2:]:
            output.add_page(page)

        final_buffer = io.BytesIO()
        output.write(final_buffer)

        # Botão de download
        st.download_button("📥 Baixar PDF final", data=final_buffer.getvalue(), file_name=output_alta)

    except Exception as e:
        st.error(f"Erro ao processar o PDF: {e}")
