from django.db import models
from django.db.models.signals import pre_save # Usamos pre_save para capturar el stock anterior
from django.dispatch import receiver

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

class Item(models.Model):
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.CASCADE, related_name='items')
    nombre = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    #Minimun Stock - Used for alerts
    stock_minimo = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen Referencial")

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
            Transaccion.objects.create(
                item=instance,
                tipo=tipo,
                cantidad=diferencia,
                stock_previo=obj_antiguo.stock,
                stock_nuevo=instance.stock
            )