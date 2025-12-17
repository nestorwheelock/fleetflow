# S-028: Onboarding y Configuración de Inquilino

**Tipo de Historia**: Historia de Usuario
**Prioridad**: Crítica
**Estimación**: 2 días
**Sprint**: Época 1
**Estado**: Pendiente

## Historia de Usuario
**Como** propietario de negocio de alquiler de autos
**Quiero** registrarme y configurar mi negocio de alquiler en FleetFlow
**Para que** pueda comenzar a gestionar mi flota sin configuración técnica

## Criterios de Aceptación
- [ ] Puede registrarse con email y contraseña
- [ ] Puede elegir un subdominio (nombre-empresa.tudominio.com)
- [ ] Puede ingresar información del negocio (nombre, dirección, teléfono, email)
- [ ] Puede subir logo de la empresa
- [ ] Puede seleccionar plan de suscripción (Inicial, Pro, Empresarial)
- [ ] Prueba gratuita de 14 días activada automáticamente
- [ ] Recibe email de bienvenida con guía de inicio
- [ ] Asistente de configuración guiado para primer vehículo y cliente

## Flujo de Usuario
1. Visitar página de registro
2. Ingresar email, contraseña, nombre del negocio
3. Elegir subdominio (verificar disponibilidad)
4. Seleccionar plan de suscripción
5. Ingresar detalles del negocio
6. Subir logo (opcional)
7. Iniciar prueba gratuita
8. Redirigido al asistente de configuración

## Definición de Terminado
- [ ] Formulario de registro con validación implementado
- [ ] Verificador de disponibilidad de subdominio (AJAX) funcionando
- [ ] Inquilino creado con estado de prueba
- [ ] Cuenta de usuario propietario creada
- [ ] Email de bienvenida enviado vía SendGrid/SES
- [ ] Asistente de configuración guía primeros pasos
- [ ] Pruebas cubren flujo de registro (>95% cobertura)
- [ ] Documentación del proceso de onboarding
