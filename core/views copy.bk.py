from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.http import JsonResponse
from .models import Item, Transaccion, Categoria, Subcategoria
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages # Para enviar alertas al usuario
from datetime import datetime

# Create your views here.
@login_required
def lista_inventario(request):
    busqueda = request.GET.get('buscar') # Captura lo que el usuario escribe
    items = Item.objects.all()

    if busqueda:
        items = items.filter(
            Q(nombre__icontains=busqueda) | 
            Q(sku__icontains=busqueda)
        )

    return render(request, 'core/lista_inventario.html', {'items': items, 'busqueda': busqueda})

# Función para el botón de salida rápida (-1)
@login_required
def salida_rapida(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    if item.stock > 0:
        item.stock -= 1
        item.save() # Esto dispara automáticamente la señal que creamos antes
    return redirect('lista_inventario')

# Vista para ver todos los movimientos
@login_required
def historial_movimientos(request):
    movimientos = Transaccion.objects.all().order_by('-fecha')
    return render(request, 'core/historial.html', {'movimientos': movimientos})

from django.shortcuts import render, get_object_or_404, redirect
from .models import Item, Transaccion
from django import forms

class SubcategoriaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre}" # Forzamos que devuelva solo el nombre

class CategoriaChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.nombre}"

# Creamos un formulario rápido para editar el ítem
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nombre', 'sku', 'stock', 'stock_minimo', 'descripcion', 'imagen'] # Agregados aquí
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre']
        widgets = {'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Electrónica'})}

class SubcategoriaForm(forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['categoria', 'nombre']
        widgets = {
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Laptops'})
        }
@login_required
def detalle_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    # Obtenemos solo las transacciones de ESTE ítem
    movimientos = item.transacciones.all().order_by('-fecha')
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('detalle_item', item_id=item.id)
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'core/detalle_item.html', {
        'item': item,
        'form': form,
        'movimientos': movimientos
    })



@login_required
def detalle_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    movimientos = item.transacciones.all().order_by('-fecha')[:10]
    
    if request.method == 'POST':
        # Pasamos la instancia actual para que Django sepa qué editar
        form = ItemForm(request.POST, request.FILES, instance=item)
        # Agregamos request.FILES para que la imagen se procese
        if form.is_valid():
            form.save()
            return redirect('detalle_item', item_id=item.id)
        else:
            # ESTO ES CLAVE: Si no se guarda, imprime los errores en tu terminal 
            # para que sepamos qué campo está protestando.
            print(form.errors) 
    else:
        form = ItemForm(instance=item)
    
    return render(request, 'core/detalle_item.html', {
        'item': item,
        'form': form,
        'movimientos': movimientos
    })

@login_required
def crear_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            nuevo_item = form.save()
            return redirect('detalle_item', item_id=nuevo_item.id)
    else:
        form = ItemForm()
    
    return render(request, 'core/crear_item.html', {'form': form})

def cargar_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = Subcategoria.objects.filter(categoria_id=categoria_id).values('id', 'nombre')
    return JsonResponse(list(subcategorias), safe=False)

def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ESTO ES CLAVE: Forzamos el widget y las clases de nuevo
        self.fields['categoria'].widget.attrs.update({'class': 'form-select'})
        self.fields['subcategoria'].widget.attrs.update({'class': 'form-select'})
        
        if self.instance and self.instance.pk:
            # Sincronizamos la categoría con la subcategoría que ya tiene el ítem
            self.fields['categoria'].initial = self.instance.subcategoria.categoria.id

@login_required
def gestionar_categorias(request):
    categorias = Categoria.objects.all().prefetch_related('subcategorias')
    form_cat = CategoriaForm()
    form_sub = SubcategoriaForm()

    if request.method == 'POST':
        if 'btn_cat' in request.POST:
            form_cat = CategoriaForm(request.POST)
            if form_cat.is_valid():
                form_cat.save()
                return redirect('gestionar_categorias')
        elif 'btn_sub' in request.POST:
            form_sub = SubcategoriaForm(request.POST)
            if form_sub.is_valid():
                form_sub.save()
                return redirect('gestionar_categorias')

    return render(request, 'core/gestionar_categorias.html', {
        'categorias': categorias,
        'form_cat': form_cat,
        'form_sub': form_sub
    })

@login_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('gestionar_categorias')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'core/editar_clasificacion.html', {'form': form, 'titulo': 'Editar Categoría'})

@login_required
def editar_subcategoria(request, pk):
    subcategoria = get_object_or_404(Subcategoria, pk=pk)
    if request.method == 'POST':
        form = SubcategoriaForm(request.POST, instance=subcategoria)
        if form.is_valid():
            form.save()
            return redirect('gestionar_categorias')
    else:
        form = SubcategoriaForm(instance=subcategoria)
    return render(request, 'core/editar_clasificacion.html', {'form': form, 'titulo': 'Editar Subcategoría'})

@login_required
def home_categorias(request):
    # Traemos las categorías. El conteo de subcategorías lo hace el template
    # con cat.subcategorias.count, que es mucho más seguro.
    categorias = Categoria.objects.all()
    return render(request, 'core/home_categorias.html', {'categorias': categorias})

@login_required
def items_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
    subcategorias = categoria.subcategorias.all()
    
    
    # Filtramos los items que pertenecen a las subcategorías de ESTA categoría
    items = Item.objects.filter(subcategoria__categoria=categoria)
    items_totales_count = items.count() # Para el botón "Ver Todo"
    
    # Si el usuario hizo clic en una subcategoría específica
    sub_id = request.GET.get('subcategoria')
    if sub_id:
        items = items.filter(subcategoria_id=sub_id)
        
    return render(request, 'core/items_por_categoria.html', {
        'categoria': categoria,
        'subcategoria': subcategoria_id, # Agregamos esta línea en singular
        'subcategorias': subcategorias,
        'items': items,
        'sub_seleccionada': sub_id,
        'items_totales_count': items_totales_count
    })

@login_required
def registrar_movimiento(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        cantidad = int(request.POST.get('cantidad'))
        
        # --- VALIDACIÓN DE SEGURIDAD ---
        if tipo == 'SALIDA' and cantidad > item.stock:
            messages.error(request, f"⚠️ Error: No puedes retirar {cantidad} unidades. El stock actual es de solo {item.stock}.")
            return redirect('detalle_item', item_id=item.id)
        # -------------------------------

        # Si pasa la validación, procedemos a guardar
        stock_previo = item.stock
        if tipo == 'ENTRADA':
            item.stock += cantidad
        elif tipo == 'SALIDA':
            item.stock -= cantidad
            
        item.save()
        
        # Registrar la transacción en el historial
        Transaccion.objects.create(
            item=item,
            tipo=tipo,
            cantidad=cantidad,
            stock_previo=stock_previo,
            stock_nuevo=item.stock,
            usuario=request.user.username
        )
        
        messages.success(request, f"Stock actualizado: {item.nombre} ahora tiene {item.stock} unidades.")
        return redirect(request.META.get('HTTP_REFERER', 'home_categorias'))


@login_required
def despacho_multiple(request):
    items = Item.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_id[]')
        cantidades = request.POST.getlist('cantidad[]')
        errores = []

        for i_id, cant in zip(item_ids, cantidades):
            if i_id and cant:
                item = get_object_or_404(Item, id=i_id)
                cantidad = int(cant)
                
                if cantidad > item.stock:
                    errores.append(f"{item.nombre} (Stock insuficiente: {item.stock})")
                    continue # Salta este item y sigue con el próximo

                # Lógica de descuento
                stock_previo = item.stock
                item.stock -= cantidad
                item.save()
                
                Transaccion.objects.create(
                    item=item, tipo='SALIDA', cantidad=cantidad,
                    stock_previo=stock_previo, stock_nuevo=item.stock,
                    usuario=request.user.username
                )

        if errores:
            messages.warning(request, f"Se procesaron los cambios, pero hubo problemas con: {', '.join(errores)}")
        else:
            messages.success(request, "Todo el despacho se registró correctamente.")
            
        return redirect('home_categorias')

    return render(request, 'core/despacho_multiple.html', {'items': items})

@login_required
def reporte_subcategoria(request, subcategoria_id):
    subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id)
    items = Item.objects.filter(subcategoria=subcategoria).order_by('nombre')
    
    
    context = {
        'subcategoria': subcategoria,
        'items': items,
        'fecha': datetime.now()
    }
    return render(request, 'core/reporte_pdf.html', context)