from django.contrib import admin
from .models import Categoria, Subcategoria, Item, Transaccion
# Register your models here.

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    # Columnas que verás en la lista principal
    list_display = ('nombre','sku', 'get_categoria', 'subcategoria', 'stock')
    
    # Filtros laterales para navegar rápido
    list_filter = ('subcategoria__categoria', 'subcategoria')
    
    # Buscador por nombre y SKU
    search_fields = ('nombre', 'sku')
    
    # Esto permite editar el stock directamente desde la lista sin entrar al producto
    list_editable = ('stock',)

    # Método para mostrar la Categoría padre en la lista de Items
    def get_categoria(self, obj):
        return obj.subcategoria.categoria
    get_categoria.short_description = 'Categoría'

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('item', 'tipo', 'cantidad', 'stock_previo', 'stock_nuevo', 'fecha')
    list_filter = ('tipo', 'fecha')
    readonly_fields = ('item', 'tipo', 'cantidad', 'stock_previo', 'stock_nuevo', 'fecha') # No permitir editar logs