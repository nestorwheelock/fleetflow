# S-031: Facturación de Suscripciones Stripe

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Crítica
**Estimación**: 3 días
**Sprint**: Época 2
**Estado**: Pendiente

## Historia de Usuario
**Como** propietario de negocio de alquiler de autos
**Quiero** pagar mi suscripción de FleetFlow vía Stripe
**Para que** pueda usar la plataforma con facturación mensual automática

## Criterios de Aceptación
- [ ] Puede ingresar tarjeta de crédito vía Stripe Elements
- [ ] Puede suscribirse a cualquier plan (Inicial, Pro, Empresarial)
- [ ] Puede actualizar/degradar plan
- [ ] Puede ver historial de facturación y facturas
- [ ] Puede actualizar método de pago
- [ ] Puede cancelar suscripción (fin del período de facturación)
- [ ] Recibe emails de factura de Stripe
- [ ] Pagos fallidos activan emails de recordatorio

## Integración Stripe
- [ ] Stripe Customer creado en registro
- [ ] Stripe Subscription creada en selección de plan
- [ ] Manejo de webhooks para eventos de suscripción
- [ ] Portal de cliente para facturación de autoservicio
- [ ] Prorrateo en cambios de plan
- [ ] Período de gracia para pagos fallidos (7 días)

## Eventos Webhook a Manejar
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`
- `customer.updated`

## Definición de Terminado
- [ ] SDK de Stripe integrado
- [ ] Flujo de checkout con Stripe Elements implementado
- [ ] Endpoint de webhook con verificación de firma funcionando
- [ ] Página de configuración de facturación para propietarios
- [ ] Pruebas cubren escenarios de facturación (>95% cobertura)
- [ ] Documentación de configuración de Stripe
