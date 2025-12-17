# FleetFlow - Resumen SPEC

## Referencia Rápida

| Elemento | Valor |
|----------|-------|
| **Nombre del Proyecto** | FleetFlow - SaaS de Gestión de Alquiler de Vehículos |
| **Modelo de Negocio** | Software como Servicio (Suscripción Mensual) |
| **Tecnología** | Django 5.x + PostgreSQL + Tailwind CSS + HTMX |
| **Mercado Objetivo** | Pequeños alquileres de autos (10-50 vehículos) |
| **Precios** | $99 - $349/mes (4 niveles) |
| **Épocas** | 5 (Principal, Reservas, Avanzado, Móvil, Plataforma) |
| **Historias de Usuario** | 34 total (S-001 a S-034) |
| **Tareas (Época 1)** | 28 tareas |
| **Wireframes** | 27+ pantallas |

---

## Precios de Suscripción

| Plan | Vehículos | Precio | Características Clave |
|------|-----------|--------|----------------------|
| **Inicial** | 1-10 | $99/mes | Características principales, 1 usuario |
| **Profesional** | 11-25 | $199/mes | + Reservas en línea, 3 usuarios |
| **Empresarial** | 26-50 | $349/mes | + GPS, análisis, 10 usuarios |
| **Corporativo** | 50+ | Personalizado | Ilimitado, soporte dedicado |

---

## Resumen de Épocas

### Época 1: Operaciones Principales (MVP)
**Meta**: Plataforma multi-inquilino con gestión de alquiler principal

| Historia | Descripción |
|----------|-------------|
| S-027 | Arquitectura Multi-Inquilino |
| S-028 | Onboarding y Configuración de Inquilino |
| S-029 | Gestión de Usuarios y Roles |
| S-030 | Límites de Plan y Banderas de Características |
| S-001 | Gestión de Flota de Vehículos |
| S-002 | Gestión de Clientes |
| S-003 | Sistema de Calendario de Reservaciones |
| S-004 | Flujo de Alquiler (Check-out/Check-in) |
| S-005 | Generación Básica de Contratos |
| S-006 | Panel del Personal |

### Época 2: Reservas en Línea y Pagos
**Meta**: Portal del cliente, pagos y facturación de suscripciones

| Historia | Descripción |
|----------|-------------|
| S-031 | Facturación de Suscripciones Stripe |
| S-032 | Seguimiento de Uso y Excedentes |
| S-007 | Portal de Autoservicio del Cliente |
| S-008 | Navegación de Vehículos en Línea |
| S-009 | Reservas en Línea |
| S-010 | Integración de Pagos PayPal |
| S-011 | Firma Electrónica de Contratos |
| S-012 | Notificaciones al Cliente |

### Época 3: Características Avanzadas e Integraciones
**Meta**: Mantenimiento, rastreo GPS, análisis

| Historia | Descripción |
|----------|-------------|
| S-013 | Sistema de Programación de Mantenimiento |
| S-014 | Integración GPS/Telemática |
| S-015 | Verificación de Licencia de Conducir |
| S-016 | Integración de Seguros |
| S-017 | Panel de Reportes y Análisis |
| S-018 | Experiencia Optimizada para Móvil |

### Época 4: App Móvil con Rastreo de Conductor
**Meta**: App móvil nativa para clientes finales

| Historia | Descripción |
|----------|-------------|
| S-019 | Autenticación Móvil del Cliente |
| S-020 | Navegación y Reserva Móvil de Vehículos |
| S-021 | Panel de Mis Alquileres |
| S-022 | Rastreo de Ubicación de Vehículos en Tiempo Real |
| S-023 | Compartir Viaje para Seguridad |
| S-024 | Notificaciones Push |
| S-025 | Modo Sin Conexión y Sincronización |
| S-026 | Documentos Digitales de Alquiler |

### Época 5: Plataforma y Crecimiento
**Meta**: Herramientas de administración, API, marca blanca

| Historia | Descripción |
|----------|-------------|
| S-033 | Panel de Super Administrador |
| S-034 | API Pública |
| Futuro | Opciones de Marca Blanca |
| Futuro | Marketplace de Complementos |

---

## Modelos Clave (SaaS)

### Inquilino (Nuevo)
- name, slug (subdominio)
- owner (FK a Usuario)
- plan, stripe_customer_id, stripe_subscription_id
- vehicle_limit, user_limit, features (JSON)
- business_name, address, phone, email, logo
- timezone, currency
- is_active, trial_ends_at

### Vehículo (Con Alcance de Inquilino)
- tenant (FK)
- make, model, year, vin, license_plate
- color, mileage, fuel_type, transmission, seats
- category, features (JSON), daily_rate, weekly_rate, monthly_rate
- status: available, rented, maintenance, retired

### Cliente (Con Alcance de Inquilino)
- tenant (FK)
- first_name, last_name, email, phone
- address, city, state, zip_code
- license_number, license_state, license_expiry
- verified, flag (vip/banned/none)

### Reservación (Con Alcance de Inquilino)
- tenant (FK)
- confirmation_number, vehicle (FK), customer (FK)
- pickup_date/time, return_date/time
- daily_rate, subtotal, tax_amount, total_amount
- status: pending, confirmed, in_progress, completed, cancelled

---

## Stack Tecnológico

### Backend
- Django 5.x (Multi-inquilino)
- PostgreSQL 15
- Django REST Framework
- Celery + Redis

### Frontend (Web)
- Django Templates
- Tailwind CSS
- HTMX
- Alpine.js

### Móvil (Época 4)
- React Native + Expo
- MapBox/Google Maps SDK
- Firebase Cloud Messaging

### Pagos y Facturación
- Stripe (suscripciones SaaS)
- PayPal (pagos de alquiler)

### Infraestructura
- AWS (ECS, RDS, S3, CloudFront)
- SendGrid / AWS SES (Email)
- Sentry (Monitoreo)

---

## Acceso a Características por Plan

| Característica | Inicial | Pro | Empresarial | Corporativo |
|----------------|---------|-----|-------------|-------------|
| Vehículos | 10 | 25 | 50 | Ilimitado |
| Usuarios | 1 | 3 | 10 | Ilimitado |
| Reservas en Línea | ❌ | ✅ | ✅ | ✅ |
| Pagos PayPal | ❌ | ✅ | ✅ | ✅ |
| Rastreo GPS | ❌ | ❌ | ✅ | ✅ |
| Análisis | Básico | Estándar | Avanzado | Personalizado |
| Acceso API | ❌ | ❌ | ✅ | ✅ |
| Dominio Personalizado | ❌ | ❌ | ✅ | ✅ |

---

## Metas de Ingresos

| Métrica | Año 1 | Año 2 |
|---------|-------|-------|
| Clientes | 50 | 150 |
| MRR | $10,000 | $35,000 |
| ARR | $120,000 | $420,000 |
| Abandono | <5%/mes | <3%/mes |

---

## Enlaces de Documentos

### Documentos de Planificación
- [Carta del Proyecto](PROJECT_CHARTER.md)
- [Historias de Usuario](stories/)
- [Documentos de Tareas](../tasks/)
- [Wireframes](../wireframes/)

### Nuevas Historias SaaS
- [S-027 Arquitectura Multi-Inquilino](stories/S-027-arquitectura-multi-inquilino.md)
- [S-028 Onboarding de Inquilino](stories/S-028-onboarding-inquilino.md)
- [S-029 Gestión de Usuarios](stories/S-029-gestion-usuarios.md)
- [S-030 Límites de Plan](stories/S-030-limites-plan.md)
- [S-031 Facturación Stripe](stories/S-031-facturacion-stripe.md)
- [S-032 Seguimiento de Uso](stories/S-032-seguimiento-uso.md)

---

## Línea de Tiempo de Desarrollo

| Época | Duración | Enfoque |
|-------|----------|---------|
| 1 | 4 semanas | MVP Multi-inquilino |
| 2 | 4 semanas | Pagos y facturación |
| 3 | 4 semanas | GPS, análisis |
| 4 | 4 semanas | App móvil |
| 5 | Continuo | Crecimiento de plataforma |

---

## Estado de Aprobación

- [ ] Fase SPEC Completa
- [ ] Época 1 MVP Completa
- [ ] Época 2 Pagos Completa
- [ ] Lanzamiento Beta (10 clientes)
- [ ] Lanzamiento Público
- [ ] 50 Clientes Pagando
