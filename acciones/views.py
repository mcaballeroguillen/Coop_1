from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import  TemplateView, ListView, View
from django.contrib import messages
from datetime import date
from .utils import render_to_pdf
from .models import Acciones_accionista, Datos_Accionista, Temp_Acciones_accionista, Temp_Datos_Accionista
from core.models import Libro_Diario, Libro_Mayor
from caja.models import Caja
# Create your views here.

class Index(TemplateView):
    template_name = "acciones/Index.html"

class Crear_Accionista(TemplateView):
    template_name = "acciones/Nuevo_Accionista.html"

    def validar_datos(self,request):
        id = request.POST['Identidad']
        if len(id) != 13:
            messages.error(request, "Error en Identidad", "Debe medir 13")
            return False
        list= Datos_Accionista.objects.filter(Identidad=id).count()
        if list>0:
            messages.error(request, "Ya existe un accionista con esa identidad", "Ya existe")
            return  False
        return  True

    def post(self, request, *args, **kwargs):
        va = self.validar_datos(request)
        if va == False:

            return render(request, "acciones/Nuevo_Accionista.html")
        else:
            Temp_Datos_Accionista.objects.filter(Usuario=request.user.username).delete()
            Temp_Acciones_accionista.objects.filter(Usuario=request.user.username).delete()
            A1 = Temp_Datos_Accionista(
                Nombre= request.POST['Cliente'],
                Identidad=request.POST['Identidad'],
                Fecha_Ingreso=request.POST['Fecha Ingreso'],
                Fundador=request.POST['Fundador'],
                Usuario= request.user.username

            )
            A1.save()

            Tipo_Accion = request.POST['Tipo_Apo']

            if Tipo_Accion=="reglamento":
                A2 = Temp_Acciones_accionista(
                    Usuario= request.user.username,
                    Fecha= date.today(),
                    Num_Recibo=int(request.POST['Núm. Recibo']),
                    Identidad= request.POST['Identidad'],
                    Reglamento= float(request.POST['Déposito Inicial']),
                    Extaordinaria=0.0,
                    Utilidad=0.0,
                    Donación=0.0,
                    Intereses=0.0,
                    Perdidas=0.0,
                    Total=float(request.POST['Déposito Inicial'])
                )
                A2.save()
            if Tipo_Accion=="donación":
                A2 = Temp_Acciones_accionista(
                    Usuario= request.user.username,
                    Fecha= date.today(),
                    Num_Recibo=int(request.POST['Núm. Recibo']),
                    Identidad= request.POST['Identidad'],
                    Reglamento= 0.0,
                    Extaordinaria=0.0,
                    Utilidad=0.0,
                    Donación=float(request.POST['Déposito Inicial']),
                    Intereses=0.0,
                    Perdidas=0.0,
                    Total=float(request.POST['Déposito Inicial'])
                )
                A2.save()

            if Tipo_Accion=="extraordinaria":
                A2 = Temp_Acciones_accionista(
                    Usuario= request.user.username,
                    Fecha= date.today(),
                    Num_Recibo=int(request.POST['Núm. Recibo']),
                    Identidad= request.POST['Identidad'],
                    Reglamento= 0.0,
                    Extaordinaria=float(request.POST['Déposito Inicial']),
                    Utilidad=0.0,
                    Donación=0.0,
                    Intereses=0.0,
                    Perdidas=0.0,
                    Total=float(request.POST['Déposito Inicial'])
                )
                A2.save()

        return redirect("acciones:mostrar_temp")

class Mostrar_temp(ListView):
    template_name ="acciones/Accionista_Mostrar.html"
    model = Temp_Acciones_accionista


    def get_context_data(self, *, object_list=None, **kwargs):
        ctx =super().get_context_data()
        datos = Temp_Datos_Accionista.objects.get(Usuario=self.request.user.username)

        ctx.update({
            'Cliente': datos.Nombre,
            'Identidad': datos.Identidad,
            'Fecha_Ingreso': datos.Fecha_Ingreso,
            'Fundador': datos.Fundador
        })
        return ctx
    def get_queryset(self):
        return Temp_Acciones_accionista.objects.filter(Usuario=self.request.user.username)

class generar_pdf(View):
    def get(self, request, *args, **kwargs):
        ob = Temp_Acciones_accionista.objects.filter(Usuario=request.user.username)
        presta = Temp_Datos_Accionista.objects.get(Usuario=request.user.username)

        ctx = {
            'Cliente': presta.Nombre,
            'Identidad': presta.Identidad,
            'Fecha_Ingreso': presta.Fecha_Ingreso,
            'Fundador': presta.Fundador,
            'object_list': ob
        }
        pdf= render_to_pdf('pdf/acciones_mostrar.html',ctx)
        if pdf:
            response = HttpResponse(pdf, content_type='acciones/pdf')
            filename = "Aportaciones_%s.pdf" % (presta.Nombre)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")




def guardar(request):
    datos_accionista = Temp_Datos_Accionista.objects.get(Usuario=request.user.username)
    acciones_accionista= Temp_Acciones_accionista.objects.get(Usuario=request.user.username)
    Nombre = datos_accionista.Nombre
    A1 = Datos_Accionista(
        Nombre= datos_accionista.Nombre,
        Identidad=datos_accionista.Identidad,
        Fecha_Ingreso=datos_accionista.Fecha_Ingreso,
        Fundador=datos_accionista.Fundador
    )
    A1.save()

    A2 = Acciones_accionista(
        Fecha= acciones_accionista.Fecha,
        Identidad=acciones_accionista.Identidad,
        Num_Recibo=acciones_accionista.Num_Recibo,
        Reglamento=acciones_accionista.Reglamento,
        Extaordinaria=acciones_accionista.Extaordinaria,
        Utilidad=acciones_accionista.Utilidad,
        Donación=acciones_accionista.Donación,
        Intereses=acciones_accionista.Intereses,
        Perdidas=acciones_accionista.Perdidas,
        Total=acciones_accionista.Total,
    )

    A2.save()
    cantidad_movimiento = acciones_accionista.Reglamento+ acciones_accionista.Extaordinaria+ acciones_accionista.Utilidad
    cantidad_movimiento =cantidad_movimiento+ acciones_accionista.Donación
    M1 = Libro_Diario(
        Usuario=request.user.username,
        Fecha=date.today(),
        Descripcion="Depósito Aportaciones: "+ Nombre,
        Debe= "Caja: +" + str(cantidad_movimiento),
        Haber="Aportaciones_Miembros: -" + str(cantidad_movimiento),
        Cuadre=0.0
    )
    M1.save()
    c = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").count()
    if c==0:
        M2 = Libro_Mayor(
            Cuenta="Aportaciones_Miembros",
            Debe=0.0,
            Haber=cantidad_movimiento,
            Fecha=date.today(),
            Cuadre=-cantidad_movimiento,
            Descripcion="Depósito Aportaciones: "+ Nombre
        )
        M2.save()
    else:
        cuadre = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
        M2 = Libro_Mayor(
            Cuenta="Aportaciones_Miembros",
            Debe=0.0,
            Haber=cantidad_movimiento,
            Fecha=date.today(),
            Cuadre=cuadre-cantidad_movimiento,
            Descripcion="Depósito Aportaciones: " + Nombre
        )
        M2.save()
    cuadre_caja=0.0
    c = Libro_Mayor.objects.filter(Cuenta="Caja").count()
    if c>0:
        cuadre_caja= Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
    M3 = Libro_Mayor(
        Cuenta="Caja",
        Debe=cantidad_movimiento,
        Haber=0.0,
        Cuadre=cuadre_caja+cantidad_movimiento,
        Fecha=date.today(),
        Descripcion="Depósito Aportaciones: " + Nombre


    )
    M3.save()
    M4 = Caja(
        Fecha=date.today(),
        Num_Recibo=acciones_accionista.Num_Recibo,
        Descripción="Depósito Aportaciones: " + Nombre,
        Entrada=cantidad_movimiento,
        Salida=0.0,
        Saldo=cuadre_caja+cantidad_movimiento,
    )
    M4.save()

    Temp_Acciones_accionista.objects.filter(Usuario=request.user.username).delete()
    Temp_Datos_Accionista.objects.filter(Usuario=request.user.username).delete()

    return redirect("usuarios:Libro Diario")

class Buscar_Accionista(TemplateView):
    template_name = "acciones/Buscar Accionista.html"

    def  post(self, request, *args, **kwargs):
        id = request.POST['Identidad']
        accionistas = Datos_Accionista.objects.filter(Identidad=id)
        if accionistas.count() ==0 :
            messages.error(request,"No existe accionista con esa id", 'erro de id')
            return  render(request,"acciones/Buscar Accionista.html")
        else:
            datos_accionista = Datos_Accionista.objects.get(Identidad=id)
            acciones_accionista = Acciones_accionista.objects.filter(Identidad=id)

            Temp_Acciones_accionista.objects.filter(Usuario= request.user.username).delete()
            Temp_Datos_Accionista.objects.filter(Usuario=request.user.username).delete()

            A1 = Temp_Datos_Accionista(
                Usuario= request.user.username,
                Nombre= datos_accionista.Nombre,
                Identidad=datos_accionista.Identidad,
                Fecha_Ingreso=datos_accionista.Fecha_Ingreso,
                Fundador=datos_accionista.Fundador
            )
            A1.save()
            for accion in acciones_accionista:
                A2 = Temp_Acciones_accionista(
                    Usuario= request.user.username,
                    Identidad= accion.Identidad,
                    Fecha=accion.Fecha,
                    Num_Recibo=accion.Num_Recibo,
                    Reglamento=accion.Reglamento,
                    Extaordinaria=accion.Extaordinaria,
                    Utilidad=accion.Utilidad,
                    Donación=accion.Donación,
                    Intereses=accion.Intereses,
                    Perdidas=accion.Perdidas,
                    Total=accion.Total

                )
                A2.save()
            return redirect('acciones:mostrar_temp_1')


class Mostrar_temp_1(ListView):
    template_name ="acciones/Accionista_mostrar_pago.html"
    model = Temp_Acciones_accionista


    def get_context_data(self, *, object_list=None, **kwargs):
        ctx =super().get_context_data()
        datos = Temp_Datos_Accionista.objects.get(Usuario=self.request.user.username)

        ctx.update({
            'Cliente': datos.Nombre,
            'Identidad': datos.Identidad,
            'Fecha_Ingreso': datos.Fecha_Ingreso,
            'Fundador': datos.Fundador
        })
        return ctx
    def get_queryset(self):
        return Temp_Acciones_accionista.objects.filter(Usuario=self.request.user.username)

    def  post(self, request, *args, **kwargs):
        cantidad = request.POST['Cantidad']
        cantidad=str(cantidad)
        if cantidad.isdigit():
            cantidad=float(cantidad)
            if cantidad<=0:
                messages.error(request,"Cantidad no valida", "no valida")
                return redirect("acciones:mostrar_temp_1")
        else:
            messages.error(request,"Cantidad no valida","No valido")
            return redirect("acciones:mostrar_temp_1")
        recibo = request.POST['Num_Recibo']
        recibo = str(recibo)

        if recibo.isdigit():
            recibo  =int(recibo)
            if recibo<=0:
                messages.error(request,"Núm de recibo no valido","Recibo no valido")
                return redirect("acciones:mostrar_temp_1")
        else:
            messages.error(request, "Núm de recibo no valido", "Recibo no valido")
            return redirect("acciones:mostrar_temp_1")
        tipo_de_accion = request.POST['Tipo_Apo']

        saldo = Temp_Acciones_accionista.objects.filter(Usuario=request.user.username).last().Total
        datos  = Temp_Datos_Accionista.objects.get(Usuario=request.user.username)
        Nombre = datos.Nombre
        if tipo_de_accion=="reglamento":
            A1 = Temp_Acciones_accionista(
                Usuario= request.user.username,
                Identidad= datos.Identidad,
                Fecha=date.today(),
                Num_Recibo= recibo,
                Reglamento=cantidad,
                Extaordinaria=0.0,
                Utilidad=0.0,
                Donación=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo+cantidad

            )
            A1.save()

            A1 = Acciones_accionista(
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=cantidad,
                Extaordinaria=0.0,
                Utilidad=0.0,
                Donación=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo + cantidad

            )
            A1.save()

            M1 = Libro_Diario(
                Usuario= request.user.username,
                Fecha=date.today(),
                Descripcion= "Depósito Aportaciones: " + Nombre,
                Debe= "Caja: +" + str(cantidad),
                Haber="Aportaciones_Miembros: -" + str(cantidad),
                Cuadre=0.0
            )
            M1.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Aportaciones_Miembros",
                Debe=0.0,
                Haber=cantidad,
                Fecha=date.today(),
                Cuadre=cuadre-cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre
            )
            M2.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
            M3 = Libro_Mayor(
                Cuenta="Caja",
                Debe=cantidad,
                Haber=0.0,
                Fecha=date.today(),
                Cuadre=cuadre+cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre,
            )
            M3.save()

            M4 = Caja(
                Fecha=date.today(),
                Num_Recibo=recibo,
                Descripción="Depósito Aportaciones: " + Nombre,
                Entrada=cantidad,
                Salida=0.0,
                Saldo=cuadre+cantidad
            )
            M4.save()

        if tipo_de_accion=="donación":
            A1 = Temp_Acciones_accionista(
                Usuario=request.user.username,
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=0.0,
                Donación=cantidad,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo + cantidad

            )
            A1.save()

            A1 = Acciones_accionista(
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=0.0,
                Donación=cantidad,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo + cantidad

            )
            A1.save()
            M1 = Libro_Diario(
                Usuario=request.user.username,
                Fecha=date.today(),
                Descripcion="Depósito Aportaciones: " + Nombre,
                Debe="Caja: +" + str(cantidad),
                Haber="Aportaciones_Miembros: -" + str(cantidad),
                Cuadre=0.0
            )
            M1.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Aportaciones_Miembros",
                Debe=0.0,
                Haber=cantidad,
                Fecha=date.today(),
                Cuadre=cuadre - cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre
            )
            M2.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
            M3 = Libro_Mayor(
                Cuenta="Caja",
                Debe=cantidad,
                Haber=0.0,
                Fecha=date.today(),
                Cuadre=cuadre + cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre,
            )
            M3.save()
            M4 = Caja(
                Fecha=date.today(),
                Num_Recibo=recibo,
                Descripción="Depósito Aportaciones: " + Nombre,
                Entrada=cantidad,
                Salida=0.0,
                Saldo=cuadre + cantidad
            )
            M4.save()
        if tipo_de_accion=="extraordinaria":
            A1 = Temp_Acciones_accionista(
                Usuario=request.user.username,
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=cantidad,
                Donación=0.0,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo + cantidad

            )
            A1.save()

            A1 = Acciones_accionista(
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=cantidad,
                Donación=0.0,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=0.0,
                Total=saldo + cantidad

            )
            A1.save()
            M1 = Libro_Diario(
                Usuario=request.user.username,
                Fecha=date.today(),
                Descripcion="Depósito Aportaciones: " + Nombre,
                Debe="Caja: +" + str(cantidad),
                Haber="Aportaciones_Miembros: -" + str(cantidad),
                Cuadre=0.0
            )
            M1.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Aportaciones_Miembros",
                Debe=0.0,
                Haber=cantidad,
                Fecha=date.today(),
                Cuadre=cuadre - cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre
            )
            M2.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
            M3 = Libro_Mayor(
                Cuenta="Caja",
                Debe=cantidad,
                Haber=0.0,
                Fecha=date.today(),
                Cuadre=cuadre + cantidad,
                Descripcion="Depósito Aportaciones: " + Nombre,
            )
            M3.save()
            M4 = Caja(
                Fecha=date.today(),
                Num_Recibo=recibo,
                Descripción="Depósito Aportaciones: " + Nombre,
                Entrada=cantidad,
                Salida=0.0,
                Saldo=cuadre + cantidad
            )
            M4.save()
        if tipo_de_accion=="reduccion":
            if saldo < cantidad:
                messages.error(request,"No se puede retirar esa cantidad","Monto mayor a saldi")
                return redirect("acciones:mostrar_temp_1")
            A1 = Temp_Acciones_accionista(
                Usuario=request.user.username,
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=0.0,
                Donación=0.0,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=cantidad,
                Total=saldo - cantidad

            )
            A1.save()

            A1 = Acciones_accionista(
                Identidad=datos.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Reglamento=0.0,
                Extaordinaria=0.0,
                Donación=0.0,
                Utilidad=0.0,
                Intereses=0.0,
                Perdidas=cantidad,
                Total=saldo - cantidad

            )
            A1.save()
            M1 = Libro_Diario(
                Usuario=request.user.username,
                Fecha=date.today(),
                Descripcion="Retiro Aportaciones: " + Nombre,
                Debe="Aportaciones_Miembros: +" + str(cantidad),
                Haber="Caja: -" + str(cantidad),
                Cuadre=0.0
            )
            M1.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Aportaciones_Miembros",
                Debe=cantidad,
                Haber=0.0,
                Fecha=date.today(),
                Cuadre=cuadre + cantidad,
                Descripcion="Retiro Aportaciones: " + Nombre
            )
            M2.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
            M3 = Libro_Mayor(
                Cuenta="Caja",
                Debe=0.0,
                Haber=cantidad,
                Fecha=date.today(),
                Cuadre=cuadre - cantidad,
                Descripcion="Retiro Aportaciones: " + Nombre,
            )
            M3.save()

            M4 = Caja(
                Fecha=date.today(),
                Num_Recibo=recibo,
                Descripción="Retiro Acciones: " + Nombre,
                Entrada=0.0,
                Salida=cantidad,
                Saldo=cuadre-cantidad
            )
            M4.save()

        return redirect("acciones:mostrar_temp_1")