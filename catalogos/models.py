from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.forms import CharField 

class GrupoDeportivo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Deporte(models.Model):
    nombre = models.CharField(max_length=100)
    grupo = models.ForeignKey(GrupoDeportivo, on_delete=models.CASCADE, related_name="deportes")

    def __str__(self):
        return self.nombre 

    class Meta:
        verbose_name = "Deporte"
        verbose_name_plural = "Deportes"

class Metodologo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    aPaterno = models.CharField(max_length=100)
    aMaterno = models.CharField(max_length=100)
    grupos = models.ManyToManyField(GrupoDeportivo, related_name="metodologos")
    deportes = models.ManyToManyField(Deporte, related_name="metodologos")

    def __str__(self):
        return self.nombre

    
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    edadMin = models.IntegerField()
    edadMax = models.IntegerField()
    
    def __str__(self):
        return f"{self.nombre} ({self.edadMin}-{self.edadMax} años)"
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
    
class Atleta(models.Model): 
    SEXO_CHOICES = [
        ('F', 'Femenino'),
        ('M', 'Masculino'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apMaterno = models.CharField(max_length=100)
    apPaterno = models.CharField(max_length=100)
    fechaNacimiento = models.DateField()
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        default='M',  # O 'F', según cuál prefieras como predeterminado
    )
    curp = models.CharField(max_length=18, unique=True)
    rfc = models.CharField(max_length=13, unique=True)
    estadoCivil = models.CharField(max_length=20)
    tipoSangre = models.CharField(max_length=5)
    deportes = models.ManyToManyField(Deporte, related_name="atletas")  # ADD Relación muchos a muchos JCMZ
    categorias = models.ForeignKey(Categoria, on_delete=models.CASCADE, default=1)  #ADD  Relación muchos a muchos
    
    def __str__(self):
        return f"{self.nombre} {self.apPaterno} {self.apMaterno}"

    class Meta:
        verbose_name = "Atleta"
        verbose_name_plural = "Atletas"
    
class AtletaContacto(models.Model):
    atleta = models.OneToOneField(Atleta, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    calle = models.CharField(max_length=255)
    noExterior = models.CharField(max_length=10, blank=True, null=True)
    noInterior = models.CharField(max_length=10, blank=True, null=True)
    colonia = models.CharField(max_length=100)
    cp = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.atleta.nombre} - {self.telefono}"
    
    class Meta:
        verbose_name = "Contacto de Atleta"
        verbose_name_plural = "Contactos de Atleta"
    
class ResponsableAtleta(models.Model):
    atleta = models.ForeignKey(Atleta, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    parentesco = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.nombre} ({self.parentesco}) - {self.atleta.nombre}"
    class Meta:
        verbose_name = "Responsable de Atleta"
        verbose_name_plural = "Responsables de Atletas"
    
class Consultorio(models.Model):
    nombre = models.CharField(max_length=100)
    calle = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    colonia = models.CharField(max_length=100)
    cp = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    pais = models.CharField(max_length=100)
    areas = models.ManyToManyField('Area', related_name='consultorios')
    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Consultorio"
        verbose_name_plural = "Consultorios"

class Area(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    
    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = "Area"
        verbose_name_plural = "Areas"

class ProfesionalSalud(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    idArea = models.ForeignKey(Area, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=15)
    correo = models.EmailField(unique=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.idArea.nombre}"

    class Meta:
        verbose_name = "Profesional de la Salud"
        verbose_name_plural = "Profesionales de la Salud"
    
class Horario(models.Model):
    Dias_Semana = [(1, 'Lunes'), (2, 'Martes'), (3, 'Miércoles'), (4, 'Jueves'), (5, 'Viernes'), (6, 'Sábado'), (7, 'Domingo')]
    profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    dia = models.IntegerField(choices=Dias_Semana)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_cita = models.PositiveIntegerField(default=30)  # Duración en minutos
    

    def __str__(self):
        return f"{self.profesional_salud} - {self.get_dia_display()} {self.hora_inicio} - {self.hora_fin} {self.consultorio}"
        
    class Meta:
        verbose_name = "Horario"
        verbose_name_plural = "Horarios"


class SlotDisponible(models.Model):
    """Representa un slot de tiempo disponible para agendar"""
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='slots_disponibles')
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE, related_name='slots_disponibles')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE, null=True, blank=True)
    disponible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['fecha', 'hora_inicio']
        unique_together = ('consultorio', 'fecha', 'hora_inicio')
    
    def __str__(self):
        return f"Cita en el {self.area} - {self.consultorio} - {self.fecha} {self.hora_inicio}"

    class Meta:
        verbose_name = "Cita Disponible"
        verbose_name_plural = "Citas Disponibles"


class DisponibilidadTemporal(models.Model):
    """Para manejar cambios temporales en la disponibilidad regular"""
    profesional_salud = models.ForeignKey(ProfesionalSalud, on_delete=models.CASCADE)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_semana = models.JSONField()  # Ej: [1, 2, 3] para Lunes, Martes, Miércoles
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profesional_salud} - {self.fecha_inicio} al {self.fecha_fin}"

    class Meta:
        verbose_name = "Horario Temporal"
        verbose_name_plural = "Horarios Temporales"

""" Catalogos para programas de entrenamiento """
class Entrenador(models.Model): 
    SEXO_CHOICES = [
        ('F', 'Femenino'),
        ('M', 'Masculino'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apPaterno = models.CharField(max_length=100)
    apMaterno = models.CharField(max_length=100)
    fechaNacimiento = models.DateField()
    sexo = models.CharField(
        max_length=1,
        choices=SEXO_CHOICES,
        default='M',  # O 'F', según cuál prefieras como predeterminado
    )
    telefono = models.CharField(max_length=15)
    disciplinas = models.ManyToManyField(Deporte, related_name="entrenadores")  # ADD Relación muchos a muchos JCMZ
    
    
    def __str__(self):
        return f"{self.nombre} {self.apPaterno} {self.apMaterno}"

    class Meta:
        verbose_name = "Entrenador"
        verbose_name_plural = "Entrenadores"

class ProgramaEntrenamiento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    deporte = models.ForeignKey(Deporte, on_delete=models.SET_NULL, null=True)
    nivel = models.CharField(max_length=50, choices=[
        ('básico','Básico'),
        ('intermedio','Intermedio'),
        ('avanzado','Avanzado')
    ])
    objetivo = models.CharField(max_length=100)
    duracion_dias = models.IntegerField()
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE,related_name="programas_entrenamiento")
    archivo = models.FileField(upload_to='PlanesEntrenamiento/%Y/%m/%d/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.nivel})"

    class Meta:
        verbose_name = "Programa de Entrenamiento"
        verbose_name_plural = "Programas de Entrenamiento"


class SesionEntrenamiento(models.Model):
    programa = models.ForeignKey(ProgramaEntrenamiento, on_delete=models.CASCADE, related_name='sesiones')
    dia = models.IntegerField(help_text="Día relativo al inicio del programa")
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()

    def __str__(self):
        return f"{self.programa.nombre} - Día {self.dia}: {self.titulo}"
    
    class Meta:
        verbose_name = "Sesión de entrenamiento"
        verbose_name_plural = "Sesiones de entrenamiento"
        ordering = ['programa', 'dia']


class Ejercicio(models.Model):
    sesion = models.ForeignKey(SesionEntrenamiento, on_delete=models.CASCADE, related_name='ejercicios')
    nombre = models.CharField(max_length=100)
    repeticiones = models.IntegerField(null=True, blank=True)
    series = models.IntegerField(null=True, blank=True)
    duracion_segundos = models.IntegerField(null=True, blank=True)
    distancia_metros = models.FloatField(null=True, blank=True)
    peso_kg = models.FloatField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} (Sesión Día {self.sesion.dia})"
    
    class Meta:
        verbose_name = "Ejercicio"
        verbose_name_plural = "Ejercicios"
        ordering = ['sesion', 'nombre']




