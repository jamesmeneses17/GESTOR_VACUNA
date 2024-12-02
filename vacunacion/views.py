

from django.shortcuts import render, redirect, get_object_or_404
from .models import Propietario, Mascota, Vacunacion, Vacuna, HistorialVacuna, Especie
from .forms import PropietarioForm, MascotaForm, BusquedaForm, VacunaForm, EspecieForm, CitaForm
from django.http import HttpResponse
from .models import Mascota, HistorialVacuna
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
from django.shortcuts import get_object_or_404
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from django.conf import settings
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from datetime import datetime  # Importar módulo de fecha y hora
import time
from django.http import JsonResponse
# Vista de inicio
def inicio(request):
    return render(request, 'vacunacion/inicio.html')

# Vista para registrar propietario
def registrar_propietario(request):
    form = PropietarioForm()
    mensaje = None  # Variable para mostrar un mensaje después de guardar

    if request.method == 'POST':
        form = PropietarioForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "El propietario ha sido registrado con éxito."

    return render(request, 'vacunacion/registrar_propietario.html', {
        'form': form,
        'mensaje': mensaje  # Pasamos el mensaje a la plantilla
    })

# Vista para registrar una nueva cita
def registrar_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda la cita en la base de datos
            # Mostrar mensaje de éxito y esperar 4 segundos
            return JsonResponse({'mensaje': 'Cita registrada correctamente. Redirigiendo...', 'redirect': True})
    else:
        form = CitaForm()

    return render(request, 'vacunacion/registrar_cita.html', {'form': form})

# Vista para registrar mascota
def registrar_mascota(request):
    mensaje = None  # Iniciamos el mensaje vacío
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save(commit=False)  # No guardamos aún la mascota
            propietario = form.cleaned_data['cedula_propietario']
            mascota.propietario = propietario  # Asociamos el propietario con la mascota
            mascota.save()  # Ahora guardamos la mascota
            mensaje = "La mascota ha sido registrada exitosamente."
            return redirect('servicios')  # Redirigimos a la página de servicios después de guardar
    else:
        form = MascotaForm()

    return render(request, 'vacunacion/registrar_mascota.html', {'form': form, 'mensaje': mensaje})
# Vista para registrar especie
def registrar_especie(request):
    if request.method == 'POST':
        form = EspecieForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la página de inicio después de guardar
    else:
        form = EspecieForm()
    return render(request, 'vacunacion/registrar_especie.html', {'form': form})

# Vista para registrar vacuna
def registrar_vacuna(request):
    if request.method == 'POST':
        form = VacunaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inicio')  # Redirige a la página de inicio después de guardar
    else:
        form = VacunaForm()
    return render(request, 'vacunacion/registrar_vacuna.html', {'form': form})

# Vista para buscar mascota
def buscar_mascota(request):
    mascota = None
    propietario = None
    if request.method == 'GET':
        form = BusquedaForm(request.GET)
        if form.is_valid():
            id_mascota = form.cleaned_data.get('id_mascota')
            cedula_propietario = form.cleaned_data.get('cedula')

            # Búsqueda por ID de mascota
            if id_mascota:
                mascota = get_object_or_404(Mascota, id=id_mascota)
                propietario = mascota.propietario

            # Búsqueda por cédula de propietario
            elif cedula_propietario:
                propietario = get_object_or_404(Propietario, cedula=cedula_propietario)
                mascota = Mascota.objects.filter(propietario=propietario).first()

    else:
        form = BusquedaForm()
    
    return render(request, 'vacunacion/buscar_mascota.html', {
        'form': form,
        'mascota': mascota,
        'propietario': propietario
    })

# Vista para consultar el carnet de vacunación
def consultar_carnet(request):
    mascotas = None  # Lista de mascotas (inicialmente vacía)
    if request.method == 'POST':
        cedula = request.POST.get('cedula')
        if cedula:
            # Buscar al propietario por la cédula
            try:
                propietario = Propietario.objects.get(cedula=cedula)
                # Buscar las mascotas asociadas al propietario
                mascotas = Mascota.objects.filter(propietario=propietario)
            except Propietario.DoesNotExist:
                # Si no existe un propietario con esa cédula
                mascotas = None
    return render(request, 'vacunacion/consultar_carnet.html', {'mascotas': mascotas})

# Vista para mostrar el carnet de vacunación de una mascota
def carnet_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    historial_vacunas = HistorialVacuna.objects.filter(mascota=mascota).order_by('-fecha_aplicacion')
    
    for vacuna in historial_vacunas:
        vacuna.dias_restantes = vacuna.dias_hasta_proxima()

    return render(request, 'vacunacion/carnet_mascota.html', {
        'mascota': mascota,
        'historial_vacunas': historial_vacunas
    })


# Vista para descargar el carnet de vacu
def descargar_carnet_pdf(request, mascota_id):
    # Obtener la mascota y el historial
    mascota = get_object_or_404(Mascota, id=mascota_id)
    historial_vacunas = HistorialVacuna.objects.filter(mascota=mascota).order_by('-fecha_aplicacion')

    # Obtener la fecha actual
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Formato: Año-Mes-Día Hora:Minuto:Segundo

    # Crear un buffer para el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        fontSize=18,
        textColor=colors.HexColor("#007BFF"),
        fontName="Helvetica-Bold",
        alignment=1  # Centrado
    )
    date_style = ParagraphStyle(
        'Date',
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        fontName="Helvetica",
        alignment=2  # Derecha
    )

    # Ruta completa al logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    logo = Image(logo_path, width=50, height=50)

    # Crear encabezado con logo y título
    title = Paragraph(f"Carnet de Vacunación de {mascota.nombre}", title_style)
    header = Table([[logo, title]], colWidths=[50, 400])
    header.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Logo alineado a la izquierda
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Título centrado
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Alinear verticalmente al centro
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),  # Espaciado inferior
    ]))

    # Fecha de impresión (posicionada más arriba)
    date = Paragraph(f"Fecha de impresión: {fecha_actual}", date_style)

    # Contenido del PDF
    elements = [Spacer(1, 20), date, Spacer(1, 10), header, Spacer(1, 20)]

    # Información de la mascota
    info_data = [
        ['Especie', mascota.especie],
        ['Raza', mascota.raza],
        ['Fecha de Nacimiento', mascota.fecha_nacimiento.strftime('%Y-%m-%d')],
        ['Propietario', mascota.propietario]
    ]
    info_table = Table(info_data, colWidths=[150, 350])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#333333")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 24))

    # Tabla de vacunación
    header = ['Vacuna', 'Fecha de Aplicación', 'Estado', 'Próxima Vacuna', 'Notas']
    data = [header]
    for vacuna in historial_vacunas:
        proxima = f"{vacuna.fecha_proxima} (en {vacuna.dias_hasta_proxima()} días)" if vacuna.fecha_proxima else "No programada"
        data.append([
            vacuna.vacuna.nombre,
            str(vacuna.fecha_aplicacion),
            vacuna.get_estado_display(),
            proxima,
            vacuna.notas or "Sin notas"
        ])

    # Definir la tabla (fuera del bucle)
    table = Table(data, colWidths=[120, 100, 100, 120, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#007BFF")),  # Encabezado
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Filas
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#333333")),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # Bordes
    ]))

    elements.append(table)

    # Generar PDF
    doc.build(elements)
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')


# Vista para servicios
def servicios(request):
    return render(request, 'vacunacion/servicios.html')

# Vista para nosotros
def nosotros(request):
    return render(request, 'vacunacion/nosotros.html')

# Vista para clientes
def clientes(request):
    return render(request, 'vacunacion/clientes.html')

