
# /core/urls.py
from django.urls import path, include
from . import views


urlpatterns = [
  

    path('', views.dashboard, name='dashboard'),   

    path('inventario/', views.home_categorias, name='home_categorias'), # Movimos la anterior aquí
    path('salida/<int:item_id>/', views.salida_rapida, name='salida_rapida'),
    path('historial/', views.historial_movimientos, name='historial_movimientos'),
    #Items >>>
    path('item/<int:item_id>/', views.detalle_item, name='detalle_item'),
    path('item/<int:item_id>/editar/', views.editar_item, name='editar_item'),
    path('nuevo/', views.crear_item, name='crear_item'),
    # Create new with sucgategory selected
    path('nuevo/<int:subcategoria_id>/', views.crear_item, name='crear_item_subcategoria'),
    path('ajax/cargar-subcategorias/', views.cargar_subcategorias, name='ajax_cargar_subcategorias'),
    path('categorias/', views.gestionar_categorias, name='gestionar_categorias'),
    path('categoria/editar/<int:pk>/', views.editar_categoria, name='editar_categoria'),
    path('subcategoria/editar/<int:pk>/', views.editar_subcategoria, name='editar_subcategoria'),
    #path('', views.home_categorias, name='home_categorias'), # Cambiamos la raíz
    path('categoria/<int:categoria_id>/', views.items_por_categoria, name='items_por_categoria'),
    #path('', views.home_categorias, name='home_categorias'),
    path('categorias/gestion/', views.gestionar_categorias, name='gestionar_categorias'),
    path('item/<int:item_id>/movimiento/', views.registrar_movimiento, name='registrar_movimiento'),
    path('despacho-multiple/', views.despacho_multiple, name='despacho_multiple'),
    path('categoria/<int:subcategoria_id>/', views.items_por_categoria, name='items_por_categoria'),
    path('reporte/subcategoria/<int:sub_id>/', views.reporte_subcategoria, name='reporte_subcategoria'),
    # Reportes
    path('reportes/', views.panel_reportes, name='panel_reportes'),
    path('reportes/generar/<int:sub_id>/', views.reporte_subcategoria, name='reporte_subcategoria'),
    # Ruta general (carga la primera subcategoría por defecto)
    path('categoria/<int:categoria_id>/', views.items_por_categoria, name='items_por_categoria'),
    
    # Ruta específica (cuando haces clic en una del menú lateral)
    path('categoria/<int:categoria_id>/sub/<int:subcategoria_id>/', views.items_por_categoria, name='items_por_subcategoria'),
    
    path('exportar/', views.pagina_exportar_filtros, name='pagina_exportar'),
    path('exportar/excel/', views.exportar_inventario_excel, name='exportar_excel'),
]