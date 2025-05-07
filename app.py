import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import fitz  # PyMuPDF
import io

def cortar_ate_texto(imagem):
    return imagem  # Pode implementar corte aqui se desejar

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
    pix = doc.load_page(0).get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    img_cortada = cortar_ate_texto(img)

    # Usar ImageReader
    image_reader = ImageReader(img_cortada)

    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.drawImage(image_reader, x, y, width=width, height=height)
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
    st.download_button("📄 Baixar PDF final", data=final_buffer.getvalue(), file_name="relatorio_final.pdf")
