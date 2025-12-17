# S-030: Límites de Plan y Banderas de Características

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Alta
**Estimación**: 2 días
**Sprint**: Época 1
**Estado**: Pendiente

## Historia de Usuario
**Como** operador de la plataforma FleetFlow
**Quiero** aplicar límites de plan y acceso a características
**Para que** los inquilinos solo usen características incluidas en su suscripción

## Criterios de Aceptación
- [ ] Conteo de vehículos aplicado por plan (10, 25, 50, ilimitado)
- [ ] Conteo de usuarios aplicado por plan (1, 3, 10, ilimitado)
- [ ] Características habilitadas/deshabilitadas según el plan
- [ ] Mensajes amigables cuando se alcanza el límite
- [ ] Indicaciones de actualización al alcanzar límites
- [ ] Límites suaves con advertencias vs límites duros
- [ ] Cambios de plan toman efecto inmediatamente

## Matriz de Límites por Plan

| Límite | Inicial | Pro | Empresarial | Corporativo |
|--------|---------|-----|-------------|-------------|
| Vehículos | 10 | 25 | 50 | Ilimitado |
| Usuarios | 1 | 3 | 10 | Ilimitado |
| Reservas en Línea | No | Sí | Sí | Sí |
| Pagos PayPal | No | Sí | Sí | Sí |
| Rastreo GPS | No | No | Sí | Sí |
| Análisis | Básico | Estándar | Avanzado | Personalizado |
| Acceso API | No | No | Sí | Sí |
| Dominio Personalizado | No | No | Sí | Sí |

## Implementación Técnica
- [ ] Tenant.features JSONField para banderas de características
- [ ] Campos Tenant.vehicle_limit, user_limit
- [ ] PlanLimitsMixin para vistas
- [ ] Decorador @feature_required
- [ ] Utilidades de verificación de límites
- [ ] Componentes de indicación de actualización

## Definición de Terminado
- [ ] Configuración de plan en settings/base de datos
- [ ] Verificaciones de límite en operaciones de creación
- [ ] Verificaciones de bandera de características en vistas protegidas
- [ ] Indicaciones de actualización mostradas apropiadamente
- [ ] Pruebas cubren todos los escenarios de límites (>95% cobertura)
- [ ] Documentación de configuración de planes
