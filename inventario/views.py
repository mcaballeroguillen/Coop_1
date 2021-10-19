from django.shortcuts import render , redirect
from django.views.generic import  TemplateView, ListView
from prestamos.models import Variables_Generales
from django.contrib import  messages
from .models import Temp_Inventario, Inventario
from core.models import Libro_Diario, Libro_Mayor
from datetime import  date
# Create your views here.

class Index(TemplateView):
    template_name = "inventario/Index.html"
    Variables_Generales.objects.filter(variable="Inventario").delete()
    A1 = Variables_Generales(
        variable="Inventario",
        valor="0"
    )
    A1.save()

class Nuevo(TemplateView):
    template_name = "inventario/Nuevo Articulo.html"

    def Validacion(self,request):
        valor = request.POST['Valor']
        valor = str(valor)

        if valor.isdigit():
            valor= float(valor)
            if valor>0 :
                return True
            else:
                messages.error(request,"Erro en valor", "Error en valor")
                return False
        else:
            messages.error(request,"Error en valor", "Error en valor")
            return  False

    def post(self,request,*args,**kwargs):
        v=self.Validacion(request)
        if v==True:
            Temp_Inventario.objects.filter(Usuario=self.request.user.username).delete()
            A1 = Temp_Inventario(
                Usuario= self.request.user.username,
                Codigo= request.POST['Código'],
                Descripcion=request.POST['Descripción'],
                Fecha_Ingreso= request.POST['Fecha_1'],
                Valor= float(request.POST['Valor'])
            )
            A1.save()



            return  redirect("inventario:mostrar")
        else:
            return  render(request,"inventario/Nuevo Articulo.html")


class Mostrar(ListView):
    template_name = "inventario/Mostrar Articulos.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx  = super().get_context_data()
        ctx.update({
            'Fecha': date.today()
        })

        return ctx
    def get_queryset(self):
        return  Temp_Inventario.objects.filter(Usuario=self.request.user.username)

    def post(self,request, *args,**kwargs):
        Datos = Temp_Inventario.objects.get(Usuario=request.user.username)

        A1 = Inventario(
            Codigo= Datos.Codigo,
            Descripcion=Datos.Descripcion,
            Fecha_Ingreso=Datos.Fecha_Ingreso,
            Valor=Datos.Valor
        )
        A1.save()
        M1 = Libro_Diario(
            Usuario=self.request.user.username,
            Fecha=date.today(),
            Descripcion="Ingreso a inventario: " + Datos.Descripcion,
            Debe="Inventario: +" + str(Datos.Valor),
            Haber=" ",
            Cuadre=Datos.Valor
        )
        M1.save()
        saldo_inventario = 0.0
        c = Libro_Mayor.objects.filter(Cuenta="Inventario")
        if c.count() > 0:
            saldo_inventario = c.last().Cuadre

        M2 = Libro_Mayor(
            Cuenta="Inventario",
            Debe=Datos.Valor,
            Haber=0.0,
            Cuadre=saldo_inventario + Datos.Valor,
            Fecha=date.today(),
            Descripcion=Datos.Descripcion
        )
        M2.save()

        return  redirect("usuarios:Libro Diario")

class Filtrar_Fecha(TemplateView):
    template_name = "inventario/Filtrar por fechas articulos.html"

    def validacion(self,request):
        fecha_i = request.POST['Fecha_1']
        fecha_f = request.POST['Fecha_2']

        if fecha_f< fecha_i:
            messages.error(request,"Error en fechas", "Error en fechas")
            return False
        else:
            return True

    def post(self,request,*args,**kwargs):
        v= self.validacion(request)
        if v== True:
            fecha_i = request.POST['Fecha_1']
            fecha_f = request.POST['Fecha_2']
            ob = Inventario.objects.filter(Fecha_Ingreso__gte=fecha_i, Fecha_Ingreso__lte=fecha_f)
            ctx = {
                'object_list': ob
            }
            return render(request, 'inventario/Filtrar por fechas articulos.html', ctx)
        else:
            return  render(request,'inventario/Filtrar por fechas articulos.html')

class Filtrar_codigo(TemplateView):
    template_name = "inventario/Filtrar_Codigo.html"

    def post(self,request,*args,**kwargs):
        codigo = request.POST['Código']
        ob = Inventario.objects.filter(Codigo__icontains=codigo)
        ctx = {
            'object_list': ob
        }
        return  render(request,'inventario/Filtrar_Codigo.html',ctx)

