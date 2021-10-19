from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib import  messages
from .models import Temp_Caja, Caja
from datetime import  date, timedelta
from core.models import Libro_Diario, Libro_Mayor
from prestamos.models import Variables_Generales
from inventario.models import Inventario

# Create your views here.

class Index(TemplateView):
    template_name = "caja/index.html"
    Variables_Generales.objects.filter(variable="Caja").delete()
    A1=Variables_Generales(
       variable="Caja",
       valor="0"
    )
    A1.save()

class Nuevo_Accion(TemplateView):
    template_name = "caja/Nuevo Movimiento.html"

    def Valdación(self,request):
        cantidad = request.POST['Cantidad']
        cantidad =str(cantidad)
        Tipo = request.POST['Descrpción']
        caja=0.0
        if Libro_Mayor.objects.filter(Cuenta="Caja").count()>0:
            caja = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
        Saldo_Caja = float(caja)

        if cantidad.isdigit():
          cantidad = float(cantidad)
          if cantidad<=0 :
              messages.error(request,"Error en cantidad","Error en Cantidad")
              return  False
          else:
              if (cantidad> Saldo_Caja) and (Tipo=='Ban.Retiro' or Tipo=='Viaticos'):
                  messages.error(request,"No se puede retirar esa cantidad","Saldo insuficiente")
                  return False

        N_Recibo = request.POST['Núm. Recibo']
        N_Recibo = str(N_Recibo)

        if Tipo=="Compras":


            if request.POST['Código'] is None:
                messages.error(request,"Código es necesario")
                return  False

            if request.POST['Descripción_1'] is None:
                messages.error(request,"Descripción del artículo es necesario ")
                return  False
        if N_Recibo.isdigit():
            return True
        else:
            return False







    def post(self,request,*args,**kwargs):
        v= self.Valdación(request)

        if v== True:
            cantidad = float(request.POST['Cantidad'])

            caja=0.0
            if Libro_Mayor.objects.filter(Cuenta="Caja").count()>0:
                caja = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre

            Saldo_Caja =  caja
            Tipo = request.POST['Descrpción']
            Temp_Caja.objects.filter(Usuario=self.request.user.username).delete()
            N_recibo = int(request.POST['Núm. Recibo'])
            if Tipo=='Ban.Ingreso':
                A1 = Temp_Caja(
                    Usuario=self.request.user.username,
                    Num_Recibo=N_recibo,
                    Descripción="Depósito de Banco a Caja",
                    Entrada=cantidad,
                    Salida=0.0,
                    Saldo=round(Saldo_Caja+cantidad,2)
                )
                A1.save()

                Saldo_Caja = str(round(Saldo_Caja+cantidad))
            if Tipo=="Ban.Retiro":
                A1 = Temp_Caja(
                    Usuario=self.request.user.username,
                    Num_Recibo=N_recibo,
                    Descripción="Retiro de Caja a Banco",
                    Entrada=0.0,
                    Salida=cantidad,
                    Saldo=round(Saldo_Caja - cantidad, 2)
                )
                A1.save()

            if Tipo=="Viaticos":
                A1 = Temp_Caja(
                    Usuario=self.request.user.username,
                    Num_Recibo=N_recibo,
                    Descripción=request.POST['Detalle'],
                    Entrada=0.0,
                    Salida=cantidad,
                    Saldo=round(Saldo_Caja - cantidad, 2)
                )
                A1.save()

            if Tipo=="Compras":
                A1 = Temp_Caja(
                    Usuario=self.request.user.username,
                    Num_Recibo=N_recibo,
                    Descripción=request.POST['Detalle'],
                    Entrada=0.0,
                    Salida=cantidad,
                    Saldo=round(Saldo_Caja - cantidad, 2)
                )
                A1.save()
                A2 = Inventario(
                    Codigo=request.POST['Código'],
                    Descripcion=request.POST['Descripción_1'],
                    Fecha_Ingreso = date.today(),
                    Valor= cantidad
                )
                A2.save()

            Movimiento = Temp_Caja.objects.get(Usuario=self.request.user.username)

            A1 = Caja(
                Fecha=Movimiento.Fecha,
                Num_Recibo=Movimiento.Num_Recibo,
                Entrada=Movimiento.Entrada,
                Descripción=Movimiento.Descripción,
                Salida=Movimiento.Salida,
                Saldo=Movimiento.Saldo
            )
            A1.save()
#Libros
            if Tipo=='Ban.Ingreso':
                M1 = Libro_Diario(
                    Usuario=self.request.user,
                    Fecha=date.today(),
                    Descripcion=Movimiento.Descripción,
                    Debe="Caja: + " + str(Movimiento.Entrada),
                    Haber="Banco: -" + str(Movimiento.Entrada),
                    Cuadre=0.0
                )
                M1.save()
                c1 = Libro_Mayor.objects.filter(Cuenta="Banco").count()
                banco_saldo=0
                if c1>0:
                    banco_saldo=Libro_Mayor.objects.filter(Cuenta="Banco").last().Cuadre
                M2 = Libro_Mayor(
                    Cuenta="Banco",
                    Debe=0.0,
                    Haber= Movimiento.Entrada,
                    Fecha=date.today(),
                    Cuadre=banco_saldo-Movimiento.Entrada,
                    Descripcion=Movimiento.Descripción
                )
                M2.save()
                caja_saldo=0
                c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
                if c2>0:
                    caja_saldo= Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
                M3 = Libro_Mayor(
                    Cuenta="Caja",
                    Debe=Movimiento.Entrada,
                    Haber=0.0,
                    Fecha=date.today(),
                    Cuadre=caja_saldo+Movimiento.Entrada,
                    Descripcion=Movimiento.Descripción,
                )
                M3.save()

            if Tipo=="Ban.Retiro":
                M1 = Libro_Diario(
                    Usuario=self.request.user,
                    Fecha=date.today(),
                    Descripcion=Movimiento.Descripción,
                    Debe="Banco: +" + str(Movimiento.Salida),
                    Haber="Caja: - " + str(Movimiento.Salida),
                    Cuadre=0.0
                )
                M1.save()
                c1 = Libro_Mayor.objects.filter(Cuenta="Banco").count()
                banco_saldo=0
                if c1>0:
                    banco_saldo=Libro_Mayor.objects.filter(Cuenta="Banco").last().Cuadre
                M2 = Libro_Mayor(
                    Cuenta="Banco",
                    Debe=Movimiento.Salida,
                    Haber= 0.0,
                    Fecha=date.today(),
                    Cuadre=banco_saldo+Movimiento.Salida,
                    Descripcion=Movimiento.Descripción
                )
                M2.save()
                caja_saldo=0
                c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
                if c2>0:
                    caja_saldo= Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
                M3 = Libro_Mayor(
                    Cuenta="Caja",
                    Debe=0.0,
                    Haber=Movimiento.Salida,
                    Fecha=date.today(),
                    Cuadre=caja_saldo-Movimiento.Salida,
                    Descripcion=Movimiento.Descripción,
                )
                M3.save()

            if Tipo=="Viaticos":
                M1 = Libro_Diario(
                    Usuario=self.request.user,
                    Fecha=date.today(),
                    Descripcion=Movimiento.Descripción,
                    Debe="Gastos: +" + str(Movimiento.Salida),
                    Haber="Caja: - " + str(Movimiento.Salida),
                    Cuadre=0.0
                )
                M1.save()
                c1 = Libro_Mayor.objects.filter(Cuenta="Gastos").count()
                banco_saldo=0
                if c1>0:
                    banco_saldo=Libro_Mayor.objects.filter(Cuenta="Gastos").last().Cuadre
                M2 = Libro_Mayor(
                    Cuenta="Gastos",
                    Debe=Movimiento.Salida,
                    Haber= 0.0,
                    Fecha=date.today(),
                    Cuadre=banco_saldo-Movimiento.Salida,
                    Descripcion=Movimiento.Descripción
                )
                M2.save()
                caja_saldo=0
                c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
                if c2>0:
                    caja_saldo= Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
                M3 = Libro_Mayor(
                    Cuenta="Caja",
                    Debe=0.0,
                    Haber=Movimiento.Salida,
                    Fecha=date.today(),
                    Cuadre=caja_saldo-Movimiento.Salida,
                    Descripcion=Movimiento.Descripción,
                )
                M3.save()
            if Tipo == "Compras":
                M1  = Libro_Diario(
                    Usuario= self.request.user,
                    Fecha=date.today(),
                    Descripcion=Movimiento.Descripción,
                    Debe="Inventario: +" + str(Movimiento.Salida),
                    Haber="Caja: - " + str(Movimiento.Salida),
                    Cuadre=0.0
                )
                M1.save()
                c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
                caja_saldo=0.0
                if c2 > 0:
                    caja_saldo = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
                M2 = Libro_Mayor(
                    Cuenta="Caja",
                    Debe=0.0,
                    Haber=Movimiento.Salida,
                    Fecha=date.today(),
                    Cuadre=Saldo_Caja-Movimiento.Salida,
                    Descripcion= Movimiento.Descripción,
                )
                M2.save()
                inventario_saldo=0.0
                c3 = Libro_Mayor.objects.filter(Cuenta="Inventario")
                if c3.count()>0:
                    inventario_saldo= c3.last().Cuadre
                M3  = Libro_Mayor(
                    Cuenta="Inventario",
                    Debe=Movimiento.Salida,
                    Haber=0.0,
                    Fecha=date.today(),
                    Cuadre=inventario_saldo+Movimiento.Salida,
                    Descripcion= Movimiento.Descripción
                )
                M3.save()

            return redirect('caja:mostrar')

        else:
            return  render(request,"caja/Nuevo Movimiento.html")

class Mostrar_Caja(ListView):
    template_name = "caja/Mostrar Caja.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data()
        ctx.update({
            'Fecha': date.today()
        })

        return ctx

    def get_queryset(self):
        return Temp_Caja.objects.filter(Usuario=self.request.user.username, Fecha=date.today())


class Filtrar_Caja (TemplateView):
    template_name = "caja/Mostrar_Caja_Filtrada.html"

    def Valiadcion(self,request):
        Fecha_i = request.POST['Fecha_1']
        Fecha_f = request.POST['Fecha_2']
        if Fecha_i> Fecha_f :
            messages.error(request,"Error en fechas introducidas","Error Fechas")
            return False
        return True

    def post(self,request, *args, **kwargs):
        v= self.Valiadcion(request)
        if v==False:
            return render(request,"caja/Mostrar_Caja_Filtrada.html")
        else:
            Fecha_i = request.POST['Fecha_1']
            Fecha_f = request.POST['Fecha_2']
            ob = Caja.objects.filter(Fecha__gte=Fecha_i, Fecha__lte=Fecha_f)
            ctx = {
                'object_list':ob
            }
            return  render(request,"caja/Mostrar_Caja_Filtrada.html",ctx)
