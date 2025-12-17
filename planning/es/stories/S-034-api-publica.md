# S-034: API Pública

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Baja
**Estimación**: 4 días
**Sprint**: Época 5
**Estado**: Pendiente

## Historia de Usuario
**Como** propietario de negocio de alquiler de autos (plan Empresarial/Corporativo)
**Quiero** acceder a mis datos de FleetFlow vía API
**Para que** pueda integrar con mis otros sistemas de negocio

## Criterios de Aceptación
- [ ] API REST para vehículos, clientes, reservaciones
- [ ] Autenticación por clave API
- [ ] Limitación de velocidad por plan
- [ ] Documentación de API (OpenAPI/Swagger)
- [ ] Webhooks para eventos clave
- [ ] Seguimiento de uso de API
- [ ] Solo disponible en planes Empresarial/Corporativo

## Endpoints de API

### Vehículos
- `GET /api/v1/vehicles/` - Listar vehículos
- `GET /api/v1/vehicles/{id}/` - Obtener vehículo
- `POST /api/v1/vehicles/` - Crear vehículo
- `PUT /api/v1/vehicles/{id}/` - Actualizar vehículo
- `DELETE /api/v1/vehicles/{id}/` - Eliminar vehículo

### Clientes
- `GET /api/v1/customers/` - Listar clientes
- `GET /api/v1/customers/{id}/` - Obtener cliente
- `POST /api/v1/customers/` - Crear cliente
- `PUT /api/v1/customers/{id}/` - Actualizar cliente

### Reservaciones
- `GET /api/v1/reservations/` - Listar reservaciones
- `GET /api/v1/reservations/{id}/` - Obtener reservación
- `POST /api/v1/reservations/` - Crear reservación
- `PUT /api/v1/reservations/{id}/` - Actualizar reservación
- `GET /api/v1/reservations/{id}/availability/` - Verificar disponibilidad

## Webhooks
- `reservation.created`
- `reservation.updated`
- `reservation.cancelled`
- `vehicle.status_changed`
- `payment.received`

## Definición de Terminado
- [ ] Vistas de API Django REST Framework implementadas
- [ ] Sistema de autenticación por clave API funcionando
- [ ] Middleware de limitación de velocidad implementado
- [ ] Documentación OpenAPI/Swagger generada
- [ ] Sistema de entrega de webhooks funcionando
- [ ] Registro de uso de API implementado
- [ ] Pruebas cubren endpoints de API (>95% cobertura)
- [ ] Sitio de documentación de API
