# S-032: Seguimiento de Uso y Excedentes

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Media
**Estimación**: 2 días
**Sprint**: Época 2
**Estado**: Pendiente

## Historia de Usuario
**Como** operador de la plataforma FleetFlow
**Quiero** rastrear métricas de uso de inquilinos
**Para que** pueda aplicar límites e identificar oportunidades de actualización

## Criterios de Aceptación
- [ ] Rastrear conteo de vehículos por inquilino
- [ ] Rastrear conteo de usuarios por inquilino
- [ ] Rastrear conteo de reservaciones por mes
- [ ] Rastrear uso de almacenamiento por inquilino
- [ ] Panel muestra uso vs límites
- [ ] Alertas al acercarse a límites (80%, 90%)
- [ ] Historial de uso para disputas de facturación

## Métricas de Uso a Rastrear

| Métrica | Propósito |
|---------|-----------|
| Vehículos | Aplicación de límite de plan |
| Usuarios | Aplicación de límite de plan |
| Reservaciones/mes | Análisis, venta adicional |
| Almacenamiento (MB) | Facturación futura |
| Llamadas API/mes | Medición empresarial |
| Alquileres activos | Patrones de uso |

## Implementación Técnica
- [ ] Modelo UsageMetric con instantáneas diarias
- [ ] Tarea Celery para cálculo diario de uso
- [ ] Widget de panel de uso
- [ ] Sistema de alertas de umbral
- [ ] API de uso para panel de administrador

## Definición de Terminado
- [ ] Modelos de seguimiento de uso creados
- [ ] Tarea de instantánea diaria de uso funcionando
- [ ] Uso mostrado en configuración del inquilino
- [ ] Emails de alerta al 80%, 90%, 100% de límites
- [ ] Pruebas cubren seguimiento de uso (>95% cobertura)
- [ ] Documentación del sistema de uso
