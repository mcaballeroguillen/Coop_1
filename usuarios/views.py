from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model, login, logout
from django.views.generic import TemplateView, RedirectView, ListView
from core.models import Libro_Diario, Libro_Mayor, Balance_General, Estado_Resultado
from datetime import date
from django.shortcuts import render
from django.contrib import messages
# Create your views here.


class UserLoginView(LoginView):
    template_name='usuarios/user_login.html'
    redirect_authenticated_user = True


class LogoutView(RedirectView):
    pattern_name = 'home'

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        return super().get_redirect_url(*args, **kwargs)


class Paso(TemplateView):


    def get(self, request, *args, **kwargs):
        ob = Libro_Diario.objects.filter(Fecha=date.today())
        ctx = {
            'object_list': ob
        }
        return  render(request,'transactions/Libro_Diario.html',ctx)

    def post(self,request,*args,**kwargs):
        fecha = request.POST['Fecha_1']
        ob = Libro_Diario.objects.filter(Fecha=fecha)
        ctx={
            'object_list': ob
        }
        return render(request, 'transactions/Libro_Diario.html', ctx)



class Libro_Mayor_v(TemplateView):

    def get(self, request, *args, **kwargs):
        opciones_cuentas=Libro_Mayor.objects.order_by('Cuenta').values_list('Cuenta', flat=True).distinct()
        ctx={
            'opciones':opciones_cuentas
        }
        return  render(request,"transactions/Libro Mayor.html",ctx)

    def post(self, request,*args,**kwargs):
        opciones_cuentas = Libro_Mayor.objects.order_by('Cuenta').values_list('Cuenta', flat=True).distinct()
        Cuenta = request.POST['Cuenta']
        Fecha_i= request.POST['Fecha_1']
        Fecha_f = request.POST['Fecha_2']
        ob= Libro_Mayor.objects.filter(Fecha__gte=Fecha_i, Fecha__lte=Fecha_f, Cuenta=Cuenta)
        ctx={
            'opciones': opciones_cuentas,
            'object_list': ob,
            'Cuenta':Cuenta,
        }
        return  render(request,'transactions/Libro Mayor.html',ctx)

class Balance_General_view(TemplateView):

    def cargar(self):
        opciones_cuentas = Libro_Mayor.objects.order_by('Cuenta').values_list('Cuenta', flat=True).distinct()
        activos=[]
        pasivos=[]
        for cuenta in opciones_cuentas:
            saldo = round(Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre,2)
            if saldo > 0:
                activos.append(cuenta)
            if saldo <0:
                pasivos.append(cuenta)

        Balance_General.objects.all().delete()
        t_activos=0.0
        for cuenta in activos:

            saldo = round(Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre,2)
            A = Balance_General(
                Cuenta= cuenta,
                Saldo= saldo,
                Activo=0.0,
                Pasivo=0.0,
                Total=0.0
            )
            t_activos=t_activos+saldo
            A.save()
        A = Balance_General(
            Cuenta="Total Activo",
            Saldo=0.0,
            Activo=t_activos,
            Pasivo=0.0,
            Total=0.0
        )
        A.save()
        t_pasivo=0.0
        for cuenta in pasivos:
            if cuenta != "Aportaciones_Miembros":
                saldo = round(Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre, 2)
                P = Balance_General(
                    Cuenta=cuenta,
                    Activo=0.0,
                    Pasivo=0.0,
                    Saldo=(saldo),
                    Total=0.0
                )
                P.save()
                t_pasivo = t_pasivo + saldo

        P = Balance_General(
            Cuenta="Total Pasivo",
            Saldo=0.0,
            Activo=0.0,
            Pasivo=t_pasivo,
            Total=0.0,
        )
        P.save()
        Aportaciones = Libro_Mayor.objects.filter(Cuenta="Aportaciones_Miembros").last().Cuadre
        Ganancias = t_pasivo+t_activos
        P = Balance_General(
            Cuenta="Aportaciones",
            Saldo=0.0,
            Activo=0.0,
            Total=round(Aportaciones,2),
            Pasivo=0.0
        )
        P.save()
        P = Balance_General(
            Cuenta="Ganacias",
            Saldo=0.0,
            Activo=0.0,
            Total=round(Ganancias),
            Pasivo=0.0
        )
        P.save()

    def get(self, request, *args, **kwargs):
        self.cargar()
        object_list = Balance_General.objects.all()
        ctx = {
            'object_list': object_list
        }
        return render(request,'transactions/Balance_General.html',ctx)


class Estado_Resultado_view(TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request,"transactions/Estado_Resultado.html")

    def post(self, request, *args, **kwargs):
        v = self.validacion(request)
        ctx ={}
        if v==False:
            return render(request,"transactions/Estado_Resultado.html")
        else:
            opciones_cuentas = Libro_Mayor.objects.order_by('Cuenta').values_list('Cuenta', flat=True).distinct()
            activos = []
            pasivos = []
            total_rojo= 0.0
            total_amarillo=0.0
            total_verde=0.0
            for cuenta in opciones_cuentas:
                saldo = round(Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre, 2)
                if saldo > 0:
                    activos.append(cuenta)
                if saldo < 0:
                    pasivos.append(cuenta)
            Estado_Resultado.objects.all().delete()
            Fecha_1_i = request.POST['Fecha_1_i']
            Fecha_1_f = request.POST['Fecha_1_f']
            Fecha_2_i = request.POST['Fecha_2_i']
            Fecha_2_f = request.POST['Fecha_2_f']

            for cuenta in activos:
                rojo= 0.0
                amarillo=0.0
                verde=0.0
                saldo_1 = Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre
                saldo_2 = Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre
                acciones_cuenta_1  = Libro_Mayor.objects.filter(Cuenta=cuenta,Fecha__gte=Fecha_1_i, Fecha__lte=Fecha_1_f)
                if acciones_cuenta_1.count()>0:
                    saldo_1 = acciones_cuenta_1.last().Cuadre
                acciones_cuenta_2 = Libro_Mayor.objects.filter(Cuenta=cuenta,Fecha__gte=Fecha_2_i, Fecha__lte=Fecha_2_f)
                if acciones_cuenta_2.count():
                    saldo_2 = acciones_cuenta_2.last().Cuadre

                saldo  = saldo_2-saldo_1
                if saldo>0:
                    verde=saldo
                if saldo==0:
                    amarillo=0.0
                if saldo<0:
                    rojo=saldo
                A = Estado_Resultado(
                    Cuenta=cuenta,
                    Fecha_1=saldo_1,
                    Fecha_2=saldo_2,
                    Saldo=saldo,
                    Rojo=rojo,
                    Amarillo=amarillo,
                    Verde=verde
                )
                A.save()
                total_rojo=total_rojo+rojo
                total_amarillo=total_amarillo+amarillo
                total_verde=total_verde+verde




            for cuenta in pasivos:
                rojo = 0.0
                amarillo = 0.0
                verde = 0.0
                saldo_1 = Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre
                saldo_2 = Libro_Mayor.objects.filter(Cuenta=cuenta).last().Cuadre
                acciones_cuenta_1 = Libro_Mayor.objects.filter(Cuenta=cuenta, Fecha__gte=Fecha_1_i,
                                                               Fecha__lte=Fecha_1_f)
                if acciones_cuenta_1.count() > 0:
                    saldo_1 = acciones_cuenta_1.last().Cuadre
                acciones_cuenta_2 = Libro_Mayor.objects.filter(Cuenta=cuenta, Fecha__gte=Fecha_2_i,
                                                               Fecha__lte=Fecha_2_f)
                if acciones_cuenta_2.count():
                    saldo_2 = acciones_cuenta_2.last().Cuadre

                saldo = saldo_2 - saldo_1
                if saldo > 0:
                    verde = saldo
                if saldo == 0:
                    amarillo = 0.0
                if saldo < 0:
                    rojo = saldo
                A = Estado_Resultado(
                    Cuenta=cuenta,
                    Fecha_1=saldo_1,
                    Fecha_2=saldo_2,
                    Saldo=saldo,
                    Rojo=rojo,
                    Amarillo=amarillo,
                    Verde=verde
                )
                A.save()
                total_rojo = total_rojo + rojo
                total_amarillo = total_amarillo + amarillo
                total_verde = total_verde + verde
            ctx = {
                'Fecha_1': str(Fecha_1_i) + " - " + str(Fecha_1_f),
                'Fecha_2': str(Fecha_2_i) + " - " + str(Fecha_2_f),
                'object_list': Estado_Resultado.objects.all(),
                'total_r': total_rojo,
                'total_a': total_amarillo,
                'total_v': total_verde
            }
            return render(request,"transactions/Estado_Resultado.html",ctx)

    def validacion(self, request):
        Fecha_1_i = request.POST['Fecha_1_i']
        Fecha_1_f = request.POST['Fecha_1_f']
        Fecha_2_i = request.POST['Fecha_2_i']
        Fecha_2_f = request.POST['Fecha_2_f']

        if Fecha_1_i> Fecha_1_f:
            messages.error(request,"Error en Fechas 1")
            return False
        if Fecha_1_f >Fecha_2_i:
            messages.error(request, "Error en Fechas 1 y 2")
            return False
        if Fecha_2_i > Fecha_2_f:
            messages.error(request, "Error en Fechas 2")
            return False
        return  True