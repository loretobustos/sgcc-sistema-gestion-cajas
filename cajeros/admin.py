from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required  # 👈 Esto bloquea el acceso si no han iniciado sesión
def panel_control(request):
    # Aquí va el código actual de tu vista...
    return render(request, 'tu_template.html')
