# AGREGAR al final de core/views.py (y estos imports arriba del todo)
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F, Sum
from django.utils import timezone

from insumos.models import Insumo
from finanzas.models import Pago
from operaciones.models import Turno


@staff_member_required(login_url="/admin/login/")
def panel_inicio(request):
    hoy = timezone.localdate()
    contexto = {
        "turnos_hoy": Turno.objects.filter(fecha=hoy).count(),
        "cobrado_hoy": Pago.objects.filter(fecha_hora__date=hoy).aggregate(t=Sum("monto"))["t"] or 0,
        "stock_bajo": Insumo.objects.filter(activo=True, stock_actual__lte=F("stock_minimo")).count(),
    }
    return render(request, "core/panel/inicio.html", contexto)


@staff_member_required(login_url="/admin/login/")
def panel_servicios(request):
    return render(request, "core/panel/servicios.html")
