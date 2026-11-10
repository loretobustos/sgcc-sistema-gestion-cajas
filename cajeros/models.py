from django.db import models
from django.utils import timezone

class Cajero(models.Model):
    id_cajero = models.IntegerField(primary_key=True)  # Rango 01 al 70
    # CORRECCIÓN: Ahora el RUT es único y tiene el largo correcto para el formato con puntos y guion
    rut = models.CharField(max_length=15, unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=100)
    nombre_cajero = models.CharField(max_length=100)   # Nombre o C.E (EMPRESA)
    
    # Cambiamos a CharField para manejar los tres estados del semáforo
    estado = models.CharField(
        max_length=20, 
        choices=[
            ('ACTIVO', 'Activo (Verde)'),
            ('COLACION', 'En Colación (Amarillo)'),
            ('INACTIVO', 'Inactivo (Rojo)')
        ], 
        default='INACTIVO'
    )
    ingreso = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['id_cajero']

    def __str__(self):
        return f"Cajero {self.id_cajero:02d} - {self.nombre_cajero}"

class PersonalJefatura(models.Model):
    CARGOS = [
        ('ENCARGAO', 'Encargado/a de Caja'),
        ('SUPERVISOR', 'Supervisor/a'),
        ('AYUDANTE', 'Primer Ayudante'),
    ]

    id_jefatura = models.IntegerField(primary_key=True, editable=False)  # Autogenerado 1120 - 1140
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    cargo = models.CharField(max_length=20, choices=CARGOS)

    class Meta:
        ordering = ['id_jefatura']

    def save(self, *args, **kwargs):
        # Generación automática de ID dentro del rango 1120 a 1140
        if not self.id_jefatura:
            ultimo = PersonalJefatura.objects.all().order_by('-id_jefatura').first()
            if ultimo:
                nuevo_id = ultimo.id_jefatura + 1
                if nuevo_id > 1140:
                    raise ValueError("Se ha alcanzado el límite máximo de IDs de Jefatura (1140).")
                self.id_jefatura = nuevo_id
            else:
                self.id_jefatura = 1120  # ID inicial si no hay ninguno
        super().save(*args, **kwargs)

    def __str__(self):
        return f"ID {self.id_jefatura} - {self.nombre} {self.apellido} ({self.get_cargo_display()})"
    
    
class BitacoraAuditoria(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    id_admin_responsable = models.IntegerField()  # ID en rango 1120-1140
    id_cajero = models.IntegerField()
    accion = models.CharField(max_length=50)       # Ej: APERTURA, CIERRE, COLACION, EDICION
    detalle = models.TextField()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%d/%m/%Y H:%i')}] Admin #{self.id_admin_responsable} - {self.accion} (Caja {self.id_cajero})"
