from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from clientes.models import Cliente, Convenio, Empresa
from finanzas.models import Factura
from operaciones.models import OrdenTrabajo

from .serializers_empresas_facturas import (
    ConvenioSerializer,
    EmpresaSerializer,
    FacturaSerializer,
)


class EmpresaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Empresa.objects.all().order_by("-id_empresa")
    serializer_class = EmpresaSerializer


class ConvenioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Convenio.objects.select_related("empresa").all().order_by("-id_convenio")
    serializer_class = ConvenioSerializer


class FacturaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Factura.objects.select_related("cliente", "convenio__empresa", "orden")
        .all()
        .order_by("-id_factura")
    )
    serializer_class = FacturaSerializer

    @action(detail=True, methods=["post"], url_path="enviar-email")
    def enviar_email(self, request, pk=None):
        factura = self.get_object()
        destino = (
            factura.convenio.empresa.email
            if factura.convenio and factura.convenio.empresa
            else factura.cliente.email
        )
        if not destino:
            return Response(
                {"detail": "Ni la empresa del convenio ni el cliente tienen un email registrado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asunto = f"Factura {factura.numero_factura} - Rosario Estética Vehicular"
        cuerpo = (
            f"Estimado/a {factura.cliente.nombre} {factura.cliente.apellido},\n\n"
            f"Adjuntamos el detalle de su comprobante:\n"
            f"- Número de factura: {factura.numero_factura}\n"
            f"- Fecha de emisión: {factura.fecha_emision}\n"
            f"- Orden de trabajo: #{factura.orden_id}\n"
            f"- Modalidad: {factura.convenio.empresa.razon_social + ' (' + factura.convenio.tipo_facturacion + ')' if factura.convenio else 'Particular'}\n"
            f"- Total: ${factura.total}\n\n"
            f"Muchas gracias por confiar en Rosario Estética Vehicular."
        )
        remitente = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@rosarioesteticavehicular.com")
        send_mail(asunto, cuerpo, remitente, [destino], fail_silently=True)

        factura.enviada_por_email = True
        factura.save(update_fields=["enviada_por_email"])
        return Response(self.get_serializer(factura).data, status=status.HTTP_200_OK)


class ClienteOpcionesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Cliente.objects.filter(activo=True).order_by("apellido", "nombre")

    def list(self, request, *args, **kwargs):
        data = [
            {
                "id_cliente": c.id_cliente,
                "nombre_completo": f"{c.nombre} {c.apellido}",
                "email": c.email or "",
            }
            for c in self.get_queryset()
        ]
        return Response(data)


class OrdenOpcionesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = (
        OrdenTrabajo.objects.select_related(
            "ficha_tecnica__turno__cliente",
            "ficha_tecnica__turno__vehiculo",
            "ficha_tecnica__turno__servicio",
            "estado",
        )
        .all()
        .order_by("-id_orden")
    )

    def list(self, request, *args, **kwargs):
        data = []
        for o in self.get_queryset():
            turno = o.ficha_tecnica.turno
            total_detalles = o.detalles_servicio.aggregate(suma=Sum("precio"))["suma"]
            total_sugerido = total_detalles if total_detalles is not None else turno.servicio.precio
            data.append(
                {
                    "id_orden": o.id_orden,
                    "cliente_id": turno.cliente_id,
                    "cliente_nombre": f"{turno.cliente.nombre} {turno.cliente.apellido}",
                    "patente": turno.vehiculo.patente,
                    "servicio": turno.servicio.nombre_servicio,
                    "estado": str(o.estado),
                    "total_sugerido": float(total_sugerido or Decimal("0.00")),
                    "ya_facturada": o.facturas.exists(),
                }
            )
        return Response(data)
