from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import  TemplateView, ListView
from django.contrib import messages
from datetime import date
from django.views import View
from .models import  Temp_Datos_Ahorrante, Temp_Datos_Acciones_Ahorro, Acciones_Ahorros, Datos_Ahorros
from .utils import render_to_pdf
from core.models import Libro_Diario, Libro_Mayor
from caja.models import Caja
# Create your views here.

class Index(TemplateView):
    template_name= "ahorros/Index.html"


class Crear_Cuenta (TemplateView):
    template_name = "ahorros/Nuevo_Ahorrante.html"

    def validar_datos(self, request):
        identidad =  request.POST['Identidad']
        if len(identidad) != 13:
            messages.error(request, "Error en Identidad", "Debe medir 13")
            return False
        dep_inicial= request.POST['Déposito Inicial']
        dep_inicial= str(dep_inicial)
        if dep_inicial.isdigit():
            dep = float(request.POST['Déposito Inicial'])
            if dep <= 0:
                messages.error(request, "Error en Déposito Inicial", "Debe medir 13")
                return False
        else:
            messages.error(request, "Error en Déposito Inicial", "Debe medir 13")
            return False
        c= Datos_Ahorros.objects.filter(Identidad=identidad).count()
        if c>0:
            messages.error(request,"Ahorrante ya existe", "Ya existe")
            return False
        return True

    def post(self, request, *args, **kwargs):
        va = self.validar_datos(request)
        if va == False:
            c = {
                'Cliente': request.POST['Cliente'],
                'Identidad': request.POST['Identidad'],
                'Beneficiarios': request.POST['Beneficiarios'],
                'Observaciones': request.POST['Observaciones'],
                'Déposito Inicial': request.POST['Déposito Inicial']
            }
            return  render(request, "ahorros/Nuevo_Ahorrante.html",context=c)
        else:
            user= request.user.username
            Temp_Datos_Ahorrante.objects.filter(usuario=user).delete()
            Temp_Datos_Acciones_Ahorro.objects.filter(usuario=user).delete()
            A1 = Temp_Datos_Ahorrante(
                Identidad=request.POST['Identidad'],
                Nombre= request.POST['Cliente'],
                usuario=user,
                Beneficiarios= request.POST['Beneficiarios'],
                Observacions=request.POST['Observaciones'],

            )
            A1.save()
            A2 = Temp_Datos_Acciones_Ahorro(
                    Fecha= date.today(),
                    usuario=request.user.username,
                    Identidad= request.POST['Identidad'],
                    Num_Recibo=request.POST['Núm. Recibo'],
                    Deposito= float(request.POST['Déposito Inicial']),
                    Intereses= 0.0,
                    Retiro= 0.0,
                    Saldo= float(request.POST['Déposito Inicial']),

            )
            A2.save()

            return  redirect('ahorros:mostrar_temp')



class Mostrar_Temp(ListView):
    template_name = "ahorros/Ahorrante_mostrar.html"
    model = Temp_Datos_Acciones_Ahorro
    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        info = Temp_Datos_Ahorrante.objects.filter(usuario= self.request.user.username)
        pres = info[0]
        ctx.update({
            'Cliente': pres.Nombre,
            'Identidad': pres.Identidad,
            'Beneficiarios': pres.Beneficiarios,
            'Observaciones': pres.Observacions,
        })

        return ctx
    def get_queryset(self):
        user = self.request.user.username
        return  Temp_Datos_Acciones_Ahorro.objects.filter(usuario=user)


class generar_pdf(View):
    def get(self, request, *args, **kwargs):
        ob = Temp_Datos_Acciones_Ahorro.objects.filter(usuario=request.user.username)
        presta= Temp_Datos_Ahorrante.objects.filter(usuario=request.user.username)
        dato= presta[0]
        ctx = {
            'Cliente': dato.Nombre,
            'Identidad': dato.Identidad,
            'Beneficiarios': dato.Beneficiarios,
            'Observaciones': dato.Observacions,
            'object_list': ob
        }
        pdf= render_to_pdf('pdf/ahorros_mostrar.html',ctx)
        if pdf:
            response = HttpResponse(pdf, content_type='ahorros/pdf')
            filename = "Ahorros_%s.pdf" % (dato.Nombre)
            content = "inline; filename=%s" % (filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" % (filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


def guardar(request):
     datos = Temp_Datos_Ahorrante.objects.get(usuario=request.user.username)
     acciones = Temp_Datos_Acciones_Ahorro.objects.filter(usuario=request.user.username)
     Nombre = datos.Nombre
     A1 = Datos_Ahorros(
       Identidad= datos.Identidad,
       Nombre= datos.Nombre,
       Beneficiarios= datos.Beneficiarios,
       Observacions= datos.Observacions,
     )
     A1.save()

     for accion in acciones:
         A2 = Acciones_Ahorros(
             Identidad= accion.Identidad,
             Fecha= accion.Fecha,
             Num_Recibo=accion.Num_Recibo,
             Deposito= accion.Deposito,
             Intereses=accion.Intereses,
             Retiro=accion.Retiro,
             Saldo=accion.Saldo,
         )
         A2.save()

     if accion.Deposito ==0:
         M1 = Libro_Diario(
             Usuario=request.user.username,
             Fecha=date.today(),
             Descripcion= "Retiro de "+ Nombre,
             Debe= "Capital_e_intereses_en_ahorros +" + str(accion.Retiro),
             Haber= "Caja -" + str(accion.Retiro),
             Cuadre= 0.0

         )
         M1.save()

         c = Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").count()
         if c==0:
             M2 = Libro_Mayor(
                 Cuenta="Capital_e_intereses_en_ahorros",
                 Debe=float(accion.Retiro),
                 Haber=0.0,
                 Cuadre=-float(accion.Retiro),
                 Fecha=date.today(),
                 Descripcion="Retiro " + Nombre
             )
             M2.save()
         else:
            cuadre = Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Capital_e_intereses_en_ahorros",
                Debe=float(accion.Retiro),
                Haber=0.0,
                Cuadre=cuadre+float(accion.Retiro),
                Fecha=date.today(),
                Descripcion="Retiro " + Nombre
             )
            M2.save()
         saldo_caja=0.0
         c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
         if c2>0:
             saldo_caja= Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre

         M3 = Libro_Mayor(
             Cuenta="Caja",
             Debe=0.0,
             Haber=-accion.Retiro,
             Cuadre= saldo_caja-accion.Retiro,
             Fecha=date.today(),
             Descripcion="Retiro " + Nombre,
         )
         M3.save()
         M4 = Caja(
             Fecha=date.today(),
             Num_Recibo=accion.Num_Recibo,
             Descripción="Retiro " + Nombre,
             Entrada=0.0,
             Salida=accion.Retiro,
             Saldo=saldo_caja-accion.Retiro
         )
         M4.save()
     else:
         M1 = Libro_Diario(
             Usuario=request.user.username,
             Fecha=date.today(),
             Descripcion="Depósito Ahorros " + Nombre,
             Debe= "Caja +" + str(accion.Deposito),
             Haber="Capital_e_intereses_en_ahorros -" + str(accion.Deposito),
             Cuadre=0.0

         )
         M1.save()

         c = Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").count()
         if c == 0:
             M2 = Libro_Mayor(
                 Cuenta="Capital_e_intereses_en_ahorros",
                 Debe=0.0,
                 Haber=float(accion.Deposito),
                 Cuadre=-float(accion.Deposito),
                 Fecha=date.today(),
                 Descripcion="Depósito Ahorros: " + Nombre,
             )
             M2.save()
         else:
             cuadre = Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").last().Cuadre
             M2 = Libro_Mayor(
                 Cuenta="Capital_e_intereses_en_ahorros",
                 Debe=0.0,
                 Haber=float(accion.Deposito),
                 Cuadre=cuadre - float(accion.Deposito),
                 Fecha=date.today(),
                 Descripcion="Depósito Ahorros: " + Nombre,
             )
             M2.save()
         saldo_caja = 0.0
         c2 = Libro_Mayor.objects.filter(Cuenta="Caja").count()
         if c2 > 0:
             saldo_caja = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre

         M3 = Libro_Mayor(
             Cuenta="Caja",
             Debe=accion.Deposito,
             Haber=0.0,
             Cuadre=saldo_caja + accion.Deposito,
             Fecha=date.today(),
             Descripcion="Depósito Ahorros: " + Nombre,
         )
         M3.save()

     M4 = Caja(
         Fecha=date.today(),
         Num_Recibo=accion.Num_Recibo,
         Descripción="Depósito Ahorros: " + Nombre,
         Entrada=accion.Deposito,
         Salida=0.0,
         Saldo=saldo_caja + accion.Deposito
     )
     M4.save()

     return redirect("usuarios:Libro Diario")


class Buscar_Ahorrante(TemplateView):
    template_name = "ahorros/Buscar_ahorrante.html"

    def post(self, request, *args, **kwargs):
        Temp_Datos_Acciones_Ahorro.objects.filter(usuario=self.request.user.username).delete()
        Temp_Datos_Ahorrante.objects.filter(usuario=self.request.user.username).delete()
        identidad = self.request.POST['Identidad']
        c= Datos_Ahorros.objects.filter(Identidad=identidad).count()
        if c==0:
            messages.error(request,"Ahorrante no existe","Ahorrante mal")
            return  render(request,"ahorros/Buscar_ahorrante.html")
        datos = Datos_Ahorros.objects.get(Identidad=identidad)

        acciones = Acciones_Ahorros.objects.filter(Identidad=identidad)

        A1 = Temp_Datos_Ahorrante(
            usuario= request.user.username,
            Identidad=  datos.Identidad,
            Nombre= datos.Nombre,
            Beneficiarios=datos.Beneficiarios,
            Observacions=datos.Observacions

        )
        A1.save()

        for accion in acciones:
            A2 = Temp_Datos_Acciones_Ahorro(
                usuario= request.user.username,
                Identidad= accion.Identidad,
                Fecha= accion.Fecha,
                Num_Recibo=accion.Num_Recibo,
                Deposito=accion.Deposito,
                Intereses=accion.Intereses,
                Retiro=accion.Retiro,
                Saldo=accion.Saldo
            )
            A2.save()

        return redirect('ahorros:mostrar_temp_1')

class Mostrar_Temp_1(ListView):
    template_name = "ahorros/Ahorrante_mostrar_pago.html"
    model = Temp_Datos_Acciones_Ahorro
    def get_context_data(self, *, object_list=None, **kwargs):
        ctx = super().get_context_data(**kwargs)
        info = Temp_Datos_Ahorrante.objects.filter(usuario= self.request.user.username)
        pres = info[0]
        ctx.update({
            'Cliente': pres.Nombre,
            'Identidad': pres.Identidad,
            'Beneficiarios': pres.Beneficiarios,
            'Observaciones': pres.Observacions,
        })

        return ctx
    def get_queryset(self):
        user = self.request.user.username
        return  Temp_Datos_Acciones_Ahorro.objects.filter(usuario=user)

    def post(self, request, *args, **kwargs):
        acciones = Temp_Datos_Acciones_Ahorro.objects.filter(usuario=self.request.user.username)
        ultima = acciones.last()
        saldo = ultima.Saldo

        accion_a_realizar  = self.request.POST['Accion']
        cantidad_accion = float(self.request.POST['Cantidad'])
        recibo = int(self.request.POST['Num_Recibo'])
        Nombre = Temp_Datos_Ahorrante.objects.filter(usuario=request.user.username).last().Nombre
        if accion_a_realizar == 'Depositar':
            new_saldo = saldo+cantidad_accion
            A1 = Temp_Datos_Acciones_Ahorro(
                Identidad= ultima.Identidad,
                usuario= self.request.user.username,
                Fecha= date.today(),
                Num_Recibo=recibo,
                Deposito=cantidad_accion,
                Retiro=0,
                Intereses=0,
                Saldo= new_saldo,
            )
            A1.save()
            A2 = Acciones_Ahorros(
                Identidad=ultima.Identidad,
                Fecha=date.today(),
                Num_Recibo=recibo,
                Deposito=cantidad_accion,
                Retiro=0,
                Intereses=0,
                Saldo=new_saldo,
            )
            A2.save()



            M1 = Libro_Diario(
                Usuario=request.user.username,
                Fecha=date.today(),
                Descripcion="Depósito Ahorros " + Nombre,
                Debe= "Caja: +" + str(cantidad_accion),
                Haber= "Capital_e_intereses_en_ahorros:-" +str(cantidad_accion),
                Cuadre=0.0
            )
            M1.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
            M2 = Libro_Mayor(
                Cuenta="Caja",
                Debe= cantidad_accion,
                Haber=0.0,
                Fecha=date.today(),
                Cuadre=cuadre+cantidad_accion,
                Descripcion="Depósito Ahorros " + Nombre,
            )
            M2.save()
            M4 = Caja(
                Fecha=date.today(),
                Num_Recibo=recibo,
                Descripción="Depósito Ahorros " + Nombre,
                Entrada=cantidad_accion,
                Salida=0.0,
                Saldo=cuadre+cantidad_accion
            )
            M4.save()
            cuadre = Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").last().Cuadre
            M3 = Libro_Mayor(
                Cuenta="Capital_e_intereses_en_ahorros",
                Debe=0.0,
                Haber= cantidad_accion,
                Cuadre=cuadre-cantidad_accion,
                Descripcion="Depósito Ahorros " + Nombre,
                Fecha=date.today(),

            )
            M3.save()
        else:
            if cantidad_accion>saldo:
                messages.error(request, "Error, no se puede retirar esa cantidad", "Retiro mayor a saldo")
            else:
                new_saldo = saldo - cantidad_accion
                A1 = Temp_Datos_Acciones_Ahorro(
                    Identidad=ultima.Identidad,
                    usuario=self.request.user.username,
                    Fecha=date.today(),
                    Num_Recibo=recibo,
                    Deposito=0,
                    Retiro= cantidad_accion,
                    Intereses=0,
                    Saldo=new_saldo,
                )
                A1.save()
                A2 = Acciones_Ahorros(
                    Identidad=ultima.Identidad,
                    Fecha=date.today(),
                    Num_Recibo=recibo,
                    Deposito=0,
                    Retiro=cantidad_accion,
                    Intereses=0,
                    Saldo=new_saldo,
                )
                A2.save()
                M1 = Libro_Diario(
                    Usuario=request.user.username,
                    Fecha=date.today(),
                    Descripcion="Retiro Ahorros: " + Nombre,
                    Debe= "Capital_e_intereses_en_ahorros: +" + str(cantidad_accion),
                    Haber = "Caja: -" + str(cantidad_accion),
                    Cuadre=0.0
                )
                M1.save()
                cuadre = Libro_Mayor.objects.filter(Cuenta="Caja").last().Cuadre
                M2 = Libro_Mayor(
                    Cuenta="Caja",
                    Debe=0.0,
                    Haber=cantidad_accion,
                    Fecha=date.today(),
                    Cuadre=cuadre-cantidad_accion,
                    Descripcion="Retiro Ahorros: " + Nombre
                )
                M2.save()
                M4 = Caja(
                    Fecha=date.today(),
                    Num_Recibo=recibo,
                    Descripción="Retiro Ahorros: " + Nombre,
                    Entrada=0.0,
                    Salida=cantidad_accion,
                    Saldo=cuadre-cantidad_accion
                )
                M4.save()
                cuadre= Libro_Mayor.objects.filter(Cuenta="Capital_e_intereses_en_ahorros").last().Cuadre
                M3 = Libro_Mayor(
                    Cuenta="Capital_e_intereses_en_ahorros",
                    Debe=cantidad_accion,
                    Haber=0.0,
                    Fecha=date.today(),
                    Cuadre=cuadre+cantidad_accion,
                    Descripcion="Retiro Ahorros: " + Nombre
                )
                M3.save()

        return redirect('ahorros:mostrar_temp_1')

