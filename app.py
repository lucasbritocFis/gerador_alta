import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdf2image import convert_from_bytes
from PIL import Image
import io

def cortar_ate_texto(imagem):
    # Exemplo simples: retorna a imagem sem corte
    return imagem

# Interface
st.title("Gerador de Relatório com Página 2 Customizada")

nome_paciente = st.text_input("Nome do paciente")
prontuario = st.text_input("ID/Prontuário")
uploaded_pdf_modelo = st.file_uploader("PDF modelo (com pelo menos 2 páginas)", type="pdf")
uploaded_pdf_alta = st.file_uploader("PDF com relatório de alta", type="pdf")

# Parâmetros de imagem
x = st.slider("Posição X da imagem", 0, 100, 34)
y = st.slider("Posição Y da imagem", 0, 100, 28)
width = st.slider("Largura da imagem", 100, 600, 540)
height = st.slider("Altura da imagem", 100, 800, 620)

if uploaded_pdf_modelo and uploaded_pdf_alta and nome_paciente and prontuario:
    modelo = PdfReader(uploaded_pdf_modelo)
    imagens = convert_from_bytes(uploaded_pdf_alta.read(), dpi=400)
    imagem = imagens[0]
    img_cortada = cortar_ate_texto(imagem)

    buffer_img = io.BytesIO()
    img_cortada.save(buffer_img, format="JPEG")
    buffer_img.seek(0)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.drawImage(buffer_img, x, y, width=width, height=height)
    c.setFont("Helvetica", 15)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(66, 740, nome_paciente)
    c.drawString(66, 715, "ID: " + prontuario)
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
    st.download_button("Baixar PDF final", data=final_buffer.getvalue(), file_name="relatorio_final.pdf")
