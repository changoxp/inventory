from django.db import models
from django.db.models.signals import pre_save # Usamos pre_save para capturar el stock anterior
from django.dispatch import receiver
from PIL import Image
import os, uuid

# Create your models here.
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name_plural = "Categorías"

class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='subcategorias')
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.categoria.nombre} > {self.nombre}"
    class Meta:
        ordering = ['nombre']
        verbose_name_plural = "Subcategorías"
        
def path_imagen_item(instance, filename):
    extension = os.path.splitext(filename)[1]
    # Si tiene ID lo usamos, si no (es nuevo), usamos un código único temporal
    nombre = instance.id if instance.id else uuid.uuid4().hex[:10]
    return f'productos/{nombre}{extension}'

class Item(models.Model):
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='items')
    nombre = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    #Minimun Stock - Used for alerts
    stock_minimo = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    imagen = models.ImageField(upload_to=path_imagen_item, blank=True, null=True, verbose_name="Referential img")

    def save(self, *args, **kwargs):
        # 1. Guardamos el registro primero para que se cree el archivo en el disco
        super().save(*args, **kwargs)

        # 2. Si hay una imagen, procedemos a optimizarla
        if self.imagen:
            img_path = self.imagen.path
            img = Image.open(img_path)

            # Si es muy grande (ej: más de 800px de ancho o alto)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                # thumbnail mantiene la relación de aspecto (no deforma la imagen)
                img.thumbnail(output_size)
                
                # Sobreescribimos el archivo original con la versión optimizada
                # quality=85 reduce el peso significativamente sin pérdida visual notable
                img.save(img_path, quality=85, optimize=True)

    def __str__(self):
        return self.nombre
    
    class Meta:
        ordering = ['nombre']  # Orden ascendente (A-Z)

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (+)'),
        ('SALIDA', 'Salida (-)'),
        ('AJUSTE', 'Ajuste Manual'),
    ]
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField() # Puede ser negativo si es p
    stock_previo = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.CharField(max_length=100, blank=True, null=True) # Opcional: quién lo hizo

    def __str__(self):
        return f"{self.tipo} - {self.item.nombre} ({self.fecha.strftime('%d/%m/%Y %H:%M')})"

@receiver(pre_save, sender=Item)
def registrar_movimiento(sender, instance, **kwargs):
    if instance.pk: # Si el item ya existe (no es creación nueva)
        obj_antiguo = Item.objects.get(pk=instance.pk)
        diferencia = instance.stock - obj_antiguo.stock
        
        if diferencia != 0:
            tipo = 'ENTRADA' if diferencia > 0 else 'SALIDA'
            usuario_logueado = getattr(instance, '_usuario_operacion', 'System')
            Transaccion.objects.create(
                item=instance,
                tipo=tipo,
                cantidad=diferencia,
                stock_previo=obj_antiguo.stock,
                stock_nuevo=instance.stock,
                usuario=usuario_logueado
            )