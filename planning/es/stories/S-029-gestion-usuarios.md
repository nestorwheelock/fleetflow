# S-029: Gestión de Usuarios y Roles

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Alta
**Estimación**: 2 días
**Sprint**: Época 1
**Estado**: Pendiente

## Historia de Usuario
**Como** propietario de negocio de alquiler
**Quiero** gestionar cuentas del personal con diferentes niveles de permisos
**Para que** mi equipo pueda usar el sistema con acceso apropiado

## Criterios de Aceptación
- [ ] Puede invitar miembros del personal por email
- [ ] Puede asignar roles: Propietario, Gerente, Agente
- [ ] Propietarios tienen acceso completo incluyendo facturación
- [ ] Gerentes pueden gestionar vehículos, clientes, reservaciones
- [ ] Agentes solo pueden procesar alquileres (sin acceso a configuración)
- [ ] Puede desactivar cuentas del personal
- [ ] Conteo de usuarios aplicado por plan (1, 3, 10, ilimitado)
- [ ] La invitación expira después de 7 días

## Matriz de Permisos por Rol

| Permiso | Propietario | Gerente | Agente |
|---------|-------------|---------|--------|
| Facturación/Suscripción | Sí | No | No |
| Gestión de Usuarios | Sí | No | No |
| Configuración | Sí | Sí | No |
| Gestión de Vehículos | Sí | Sí | Ver |
| Gestión de Clientes | Sí | Sí | Sí |
| Reservaciones | Sí | Sí | Sí |
| Reportes | Sí | Sí | Limitado |

## Definición de Terminado
- [ ] Modelo de Usuario extendido con FK de inquilino y rol
- [ ] Sistema de invitación con tokens de email implementado
- [ ] Decoradores/mixins de permisos basados en roles funcionando
- [ ] Aplicación de límite de usuarios por plan implementada
- [ ] UI de gestión de personal para propietarios funcionando
- [ ] Pruebas cubren todos los escenarios de permisos (>95% cobertura)
- [ ] Documentación de gestión de usuarios
