import csv
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import authenticate
from .models import Cajero, PersonalJefatura, BitacoraAuditoria
from .forms import CajeroForm


def login_jefatura(request):
    """
    Autenticación de Jefatura y Validación de Rango 1120-1140 (CU01 / HU01 / RF01).
    Incluye bypass de base de datos para pruebas locales fluidas.
    """
    if request.method == 'POST':
        id_admin_input = request.POST.get('id_admin')
        password_input = request.POST.get('password')
        
        # 1. VALIDACIÓN: Verificar si los campos obligatorios vienen vacíos
        if not id_admin_input or not password_input:
            messages.error(request, "! Error: Por favor, complete el campo de la contraseña y el ID.")
            return render(request, 'cajeros/login.html')
            
        # 2. VALIDACIÓN DE ROBUSTEZ: Exigir un largo mínimo de 4 caracteres
        if len(password_input) < 4:
            messages.error(request, "! Error: Complete el campo de la contraseña (debe tener un mínimo de 4 dígitos o letras).")
            return render(request, 'cajeros/login.html')
            
        try:
            id_admin = int(id_admin_input)
            
            # 3. Validar estrictamente el rango del ID (1120 a 1140)
            if 1120 <= id_admin <= 1140:
                
                # ====================================================
                # 🚀 ACCESO COMODÍN PARA PRUEBAS (BYPASS DE BD)
                # Si colocas la clave de pruebas "admin123", pasas de inmediato
                # ====================================================
                if password_input == "admin123":
                    request.session['id_admin'] = id_admin
                    messages.success(request, f"Sesión iniciada correctamente. Bienvenido Supervisor #{id_admin}.")
                    return redirect('listado_cajeros')
                # ====================================================

                # 4. Intento normal por Base de Datos (si no usas el comodín)
                try:
                    supervisor = PersonalJefatura.objects.get(pk=id_admin)
                    if hasattr(supervisor, 'contrasena') and supervisor.contrasena != password_input:
                        messages.error(request, "! Error 403: Contraseña incorrecta.")
                        return render(request, 'cajeros/login.html')
                        
                except PersonalJefatura.DoesNotExist:
                    messages.error(request, f"! Error 403: El Supervisor #{id_admin} no existe en el sistema o use clave comodín.")
                    return render(request, 'cajeros/login.html')

                # Si el usuario sí existía en BD y su clave coincidió
                request.session['id_admin'] = id_admin
                messages.success(request, f"Sesión iniciada correctamente. Bienvenido Supervisor #{id_admin}.")
                return redirect('listado_cajeros')
            else:
                messages.error(request, "! Error 403: Identificador no autorizado para labores de administración.")
        except (TypeError, ValueError):
            messages.error(request, "! Error 403: Ingrese un ID numérico válido.")

    return render(request, 'cajeros/login.html')





def logout_jefatura(request):
    """
    Cierra la sesión del administrador activo.
    """
    if 'id_admin' in request.session:
        del request.session['id_admin']
    messages.info(request, "Sesión de administración cerrada.")
    return redirect('login_jefatura')


def listado_cajeros(request):
    """
    Dashboard Central (CU08 / HU04 / RF09).
    Muestra el semáforo y las métricas de las 70 cajas.
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    cajeros = Cajero.objects.all().order_by('id_cajero')
    
    total_cajas = 70
    activas = cajeros.filter(estado='ACTIVO').count()
    colacion = cajeros.filter(estado='COLACION').count()
    inactivas = cajeros.filter(estado='INACTIVO').count()

    context = {
        'cajeros': cajeros,
        'total_cajas': total_cajas,
        'activas': activas,
        'colacion': colacion,
        'inactivas': inactivas,
    }
    return render(request, 'cajeros/listado_cajeros.html', context)


def crear_cajero(request):
    """
    Asignación / Alta de Cajero a Puesto (CU02 / HU02).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    if request.method == 'POST':
        form = CajeroForm(request.POST)
        if form.is_valid():
            cajero = form.save()
            
            id_admin = request.session.get('id_admin')
            
            # Registrar en la bitácora de auditoría (CU12)
            BitacoraAuditoria.objects.create(
                id_admin_responsable=id_admin,
                id_cajero=cajero.id_cajero,
                accion="APERTURA",
                detalle=f"Turno iniciado para {cajero.nombre_cajero} en caja {cajero.id_cajero}"
            )
            
            messages.success(request, f"Cajero asignado exitosamente en la caja {cajero.id_cajero}.")
            return redirect('listado_cajeros')
    else:
        form = CajeroForm()
    
    return render(request, 'cajeros/form_cajero.html', {'form': form, 'titulo': 'Ingresar Cajero'})


def editar_cajero(request, pk):
    """
    Edición de metadatos en turno vigente (CU03 / HU10).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    cajero = get_object_or_404(Cajero, pk=pk)
    if request.method == 'POST':
        form = CajeroForm(request.POST, instance=cajero)
        if form.is_valid():
            form.save()
            
            id_admin = request.session.get('id_admin')
            BitacoraAuditoria.objects.create(
                id_admin_responsable=id_admin,
                id_cajero=cajero.id_cajero,
                accion="EDICION",
                detalle=f"Modificación de datos en caja {cajero.id_cajero}"
            )

            messages.success(request, f"Datos de la caja {cajero.id_cajero} actualizados correctamente.")
            return redirect('listado_cajeros')
    else:
        form = CajeroForm(instance=cajero)
        
    return render(request, 'cajeros/form_cajero.html', {'form': form, 'titulo': 'Editar Cajero', 'cajero': cajero})


def eliminar_cajero(request, pk):
    """
    Cierre y liberación individual de caja (CU05 / HU05 / RF04).
    Requiere validación de ID de jefatura (rango 1120-1140).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    cajero = get_object_or_404(Cajero, pk=pk)
    
    if request.method == 'POST':
        id_admin_input = request.POST.get('id_admin')
        
        try:
            id_admin = int(id_admin_input)
            if not (1120 <= id_admin <= 1140):
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, "! Error 403: Identificador no autorizado para labores de administración (Debe ser entre 1120 y 1140).")
            return redirect('eliminar_cajero', pk=cajero.pk)

        # Cambiar estado a Inactivo (Rojo)
        cajero.estado = 'INACTIVO'
        cajero.save()

        BitacoraAuditoria.objects.create(
            id_admin_responsable=id_admin,
            id_cajero=cajero.id_cajero,
            accion="CIERRE",
            detalle=f"Cierre de turno y liberación de caja {cajero.id_cajero}"
        )

        messages.success(request, f"Turno de la caja {cajero.id_cajero} cerrado y liberado exitosamente.")
        return redirect('listado_cajeros')

    return render(request, 'cajeros/eliminar_cajero.html', {'cajero': cajero})


def cambiar_colacion(request, pk):
    """
    Cambia el estado de una caja activa a 'En Colación / Pausa' (Amarillo) (CU04 / HU06).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    cajero = get_object_or_404(Cajero, pk=pk)
    if cajero.estado == 'ACTIVO':
        cajero.estado = 'COLACION'
        cajero.save()
        
        id_admin = request.session.get('id_admin')
        BitacoraAuditoria.objects.create(
            id_admin_responsable=id_admin,
            id_cajero=cajero.id_cajero,
            accion="COLACION",
            detalle=f"Caja {cajero.id_cajero} enviada a pausa/colación"
        )

        messages.warning(request, f"La caja {cajero.id_cajero} ha entrado en Colación (Pausa).")
    return redirect('listado_cajeros')


def reanudar_turno(request, pk):
    """
    Retorna el estado de la caja de Colación (Amarillo) a Activo (Verde) (CU04 / HU06).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    cajero = get_object_or_404(Cajero, pk=pk)
    if cajero.estado == 'COLACION':
        cajero.estado = 'ACTIVO'
        cajero.save()
        
        id_admin = request.session.get('id_admin')
        BitacoraAuditoria.objects.create(
            id_admin_responsable=id_admin,
            id_cajero=cajero.id_cajero,
            accion="REANUDAR",
            detalle=f"Caja {cajero.id_cajero} reanudada a estado activo"
        )

        messages.success(request, f"Turno de la caja {cajero.id_cajero} reanudado a Activo.")
    return redirect('listado_cajeros')


def cierre_general_jornada(request):
    """
    Finaliza simultáneamente todos los turnos activos o en colación (CU07 / HU14 / RF08).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    if request.method == 'POST':
        id_admin_input = request.POST.get('id_admin')
        
        try:
            id_admin = int(id_admin_input)
            if not (1120 <= id_admin <= 1140):
                raise ValueError()
        except (TypeError, ValueError):
            messages.error(request, "! Error 403: ID de jefatura no autorizado para cierre general.")
            return redirect('listado_cajeros')

        # Ejecución masiva
        cajas_activas = Cajero.objects.filter(estado__in=['ACTIVO', 'COLACION'])
        cantidad = cajas_activas.count()
        cajas_activas.update(estado='INACTIVO')
        
        BitacoraAuditoria.objects.create(
            id_admin_responsable=id_admin,
            id_cajero=0, 
            accion="CIERRE_GENERAL",
            detalle=f"Cierre general masivo de {cantidad} cajas ejecutado por jefatura"
        )

        messages.success(request, f"¡Cierre general ejecutado con éxito! Se cerraron {cantidad} cajas abiertas.")
        return redirect('listado_cajeros')

    return render(request, 'cajeros/cierre_general.html')


def historial_auditoria(request):
    """
    Consulta el historial de turnos y eventos de auditoría (CU13 / HU08 / RF14).
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        messages.error(request, "Acceso denegada. Debe iniciar sesión como Supervisor.")
        return redirect('login_jefatura')

    caja_filtro = request.GET.get('caja')
    if caja_filtro:
        logs = BitacoraAuditoria.objects.filter(id_cajero=caja_filtro).order_by('-timestamp')
    else:
        logs = BitacoraAuditoria.objects.all().order_by('-timestamp')
    return render(request, 'cajeros/historial.html', {'logs': logs})


def exportar_csv(request):
    """
    Genera y descarga un reporte CSV con el historial de auditoría.
    """
    # === CONTROL DE ACCESO ===
    if 'id_admin' not in request.session:
        return HttpResponse("No autorizado", status=403)
        
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_bitacora.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Fecha y Hora', 'ID Admin', 'Caja', 'Acción', 'Detalle'])
    
    logs = BitacoraAuditoria.objects.all().order_by('-timestamp')
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
            log.id_admin_responsable,
            f"Caja {log.id_cajero}" if log.id_cajero > 0 else "Masivo",
            log.accion,
            log.detalle
        ])
        
    return response
