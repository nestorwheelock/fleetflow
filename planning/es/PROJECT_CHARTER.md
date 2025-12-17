# FleetFlow - Carta del Proyecto

## Resumen del Proyecto

**Nombre del Proyecto**: FleetFlow - SaaS de Gestión de Alquiler de Vehículos
**Versión**: 1.0.0
**Modelo de Negocio**: Software como Servicio (SaaS)
**Mercado Objetivo**: Negocios pequeños y medianos de alquiler de vehículos (10-50 unidades)

---

## Resumen Ejecutivo

FleetFlow es una plataforma SaaS multi-inquilino para gestión de alquiler de vehículos, diseñada específicamente para negocios de alquiler locales y regionales. La plataforma proporciona operaciones de alquiler de extremo a extremo incluyendo gestión de flota, reservaciones, reservas en línea, pagos, contratos, seguimiento de mantenimiento y rastreo GPS de flota.

**Modelo de Negocio**: Suscripción mensual ($1,699-8,499 MXN/mes según tamaño de flota y características)

---

## Objetivos de Negocio

### Metas Principales
1. **Construir ingresos recurrentes** — Suscripciones mensuales de negocios de alquiler
2. **Capturar mercado desatendido** — Pequeños alquileres ignorados por proveedores empresariales
3. **Reducir costo de adquisición de clientes** — Registros de autoservicio, prueba gratuita
4. **Lograr rentabilidad** — 100+ clientes pagando en 12 meses
5. **Crear activo vendible** — Construir hacia adquisición a 3-5x ARR

### Métricas de Éxito

| Métrica | Meta Año 1 | Meta Año 2 |
|---------|------------|------------|
| Clientes Pagando | 50 | 150 |
| Ingresos Mensuales Recurrentes (MRR) | $170,000 MXN | $595,000 MXN |
| Ingresos Anuales Recurrentes (ARR) | $2,040,000 MXN | $7,140,000 MXN |
| Tasa de Abandono | <5%/mes | <3%/mes |
| Costo de Adquisición de Cliente | <$3,400 MXN | <$2,550 MXN |
| Valor de Vida del Cliente (LTV) | >$34,000 MXN | >$51,000 MXN |

---

## Modelo de Ingresos

### Niveles de Suscripción

| Plan | Vehículos | Precio Mensual | Precio Anual | Características |
|------|-----------|----------------|--------------|-----------------|
| **Inicial** | 1-10 | $1,699 MXN | $16,900 MXN (17% desc.) | Características principales, 1 usuario |
| **Profesional** | 11-25 | $3,399 MXN | $33,900 MXN (17% desc.) | + Reservas en línea, 3 usuarios |
| **Empresarial** | 26-50 | $5,999 MXN | $59,900 MXN (17% desc.) | + GPS, análisis, 10 usuarios |
| **Corporativo** | 50+ | Personalizado | Personalizado | Ilimitado, soporte dedicado |

### Proyecciones de Ingresos

| Escenario | Clientes | MRR Promedio | Ingresos Mensuales | Ingresos Anuales |
|-----------|----------|--------------|-------------------|------------------|
| Conservador | 50 | $2,975 MXN | $148,750 MXN | $1,785,000 MXN |
| Objetivo | 100 | $3,400 MXN | $340,000 MXN | $4,080,000 MXN |
| Optimista | 200 | $3,825 MXN | $765,000 MXN | $9,180,000 MXN |

### Economía Unitaria

| Métrica | Valor |
|---------|-------|
| Ingreso Promedio Por Usuario (ARPU) | $3,400 MXN/mes |
| Costo de Adquisición de Cliente (CAC) | $2,550 MXN |
| Valor de Vida del Cliente (LTV) | $40,800 MXN (12 meses retención promedio) |
| Ratio LTV:CAC | 16:1 |
| Margen Bruto | 80% |
| Período de Recuperación | <1 mes |

---

## Alcance

### Características de la Plataforma (5 Épocas)

**Época 1: Operaciones Principales (MVP)**
- Arquitectura multi-inquilino
- Registro y configuración de inquilinos
- Gestión de flota de vehículos
- Base de datos de clientes
- Calendario de reservaciones con prevención de conflictos
- Flujos de trabajo de check-out/check-in
- Generación de contratos PDF
- Panel de personal

**Época 2: Reservas en Línea y Pagos**
- Portal de autoservicio para clientes
- Navegación de vehículos en línea
- Reservas de autoservicio
- Procesamiento de pagos PayPal (para alquileres)
- Contratos con firma electrónica
- Notificaciones por email
- Facturación de suscripciones Stripe (para SaaS)

**Época 3: Características Avanzadas**
- Programación de mantenimiento
- Integración GPS/telemática
- API de verificación de licencias
- Panel de análisis
- Seguimiento de uso y límites

**Época 4: Aplicación Móvil**
- Aplicación móvil React Native
- Rastreo de vehículos en tiempo real
- Compartir viaje
- Notificaciones push
- Modo sin conexión

**Época 5: Plataforma y Crecimiento** *(Futuro)*
- Super panel de administración (gestionar todos los inquilinos)
- Opciones de marca blanca
- API pública
- Marketplace de complementos
- Sistema de afiliados/referidos

### Fuera del Alcance (Futuro)
- Múltiples ubicaciones por inquilino
- Gestión de franquicias
- Módulo de subasta/venta de vehículos
- Integración completa de contabilidad/ERP
- Llave digital/entrada sin llave

---

## Arquitectura Técnica

### Diseño Multi-Inquilino

```
┌─────────────────────────────────────────────────────────────────┐
│                ARQUITECTURA SAAS DE FLEETFLOW                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐          │
│   │Inquilino│  │Inquilino│  │Inquilino│  │Inquilino│          │
│   │    A    │  │    B    │  │    C    │  │    N    │          │
│   │(Empresa │  │(Empresa │  │(Empresa │  │  ...    │          │
│   │Alquiler)│  │Alquiler)│  │Alquiler)│  │         │          │
│   └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘          │
│        │            │            │            │                │
│        └────────────┼────────────┼────────────┘                │
│                     │            │                             │
│              ┌──────▼────────────▼──────┐                      │
│              │   PLATAFORMA FLEETFLOW    │                      │
│              │  (Aplicación Compartida)  │                      │
│              └──────────────┬───────────┘                      │
│                             │                                   │
│    ┌────────────────────────┼────────────────────────┐         │
│    │                        │                        │         │
│  ┌─▼───────┐         ┌──────▼──────┐          ┌─────▼─────┐   │
│  │ Datos   │         │  Servicios  │          │ Servicio  │   │
│  │Inquilino│         │ Compartidos │          │Facturación│   │
│  │(Aislado)│         │             │          │ (Stripe)  │   │
│  └─────────┘         └─────────────┘          └───────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    INFRAESTRUCTURA                       │   │
│  │  PostgreSQL │ Redis │ S3 │ Celery │ AWS                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Estrategia de Aislamiento de Inquilinos

| Componente | Método de Aislamiento |
|------------|----------------------|
| Base de Datos | BD compartida, tenant_id en todas las tablas |
| Almacenamiento de Archivos | Prefijos S3 separados por inquilino |
| Subdominios | nombre-inquilino.fleetflow.io |
| API | Inquilino identificado vía token JWT |
| Caché | Prefijos de clave Redis por inquilino |

### Stack Tecnológico

| Capa | Tecnología |
|------|------------|
| Backend | Django 5.x, Python 3.12+ |
| Base de Datos | PostgreSQL 15 (multi-inquilino) |
| Caché | Redis |
| Cola de Tareas | Celery |
| API | Django REST Framework |
| Frontend | Django Templates, Tailwind CSS, HTMX, Alpine.js |
| Móvil | React Native, Expo |
| Facturación SaaS | Stripe (suscripciones) |
| Pagos de Alquiler | PayPal |
| Hospedaje | AWS (ECS, RDS, S3, CloudFront) |
| Monitoreo | Sentry, CloudWatch |
| Email | SendGrid / AWS SES |

---

## Modelo de Datos (Multi-Inquilino)

### Modelo Principal de Inquilino

```python
class Tenant(models.Model):
    # Identidad
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)  # subdominio
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    # Suscripción (Stripe)
    plan = models.CharField(choices=PLAN_CHOICES)
    stripe_customer_id = models.CharField()
    stripe_subscription_id = models.CharField()
    subscription_status = models.CharField()  # active, past_due, canceled

    # Límites del Plan
    vehicle_limit = models.IntegerField()
    user_limit = models.IntegerField()
    features = models.JSONField()  # características habilitadas

    # Información del Negocio
    business_name = models.CharField()
    business_address = models.TextField()
    business_phone = models.CharField()
    business_email = models.EmailField()
    logo = models.ImageField()
    timezone = models.CharField()
    currency = models.CharField(default='MXN')

    # Estado
    is_active = models.BooleanField(default=True)
    trial_ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Modelos con Alcance de Inquilino

Todos los modelos de negocio incluyen clave foránea de inquilino:

```python
class TenantModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class Vehicle(TenantModel):
    # ... campos de vehículo

class Customer(TenantModel):
    # ... campos de cliente

class Reservation(TenantModel):
    # ... campos de reservación
```

---

## Acceso a Características por Plan

| Característica | Inicial | Profesional | Empresarial | Corporativo |
|----------------|---------|-------------|-------------|-------------|
| **Precio** | $1,699 MXN/mes | $3,399 MXN/mes | $5,999 MXN/mes | Personalizado |
| **Vehículos** | 10 | 25 | 50 | Ilimitado |
| **Usuarios** | 1 | 3 | 10 | Ilimitado |
| **Reservaciones** | Ilimitadas | Ilimitadas | Ilimitadas | Ilimitadas |
| **Clientes** | Ilimitados | Ilimitados | Ilimitados | Ilimitados |
| **Reservas en Línea** | ❌ | ✅ | ✅ | ✅ |
| **Pagos PayPal** | ❌ | ✅ | ✅ | ✅ |
| **Firmas Electrónicas** | ❌ | ✅ | ✅ | ✅ |
| **Rastreo GPS** | ❌ | ❌ | ✅ | ✅ |
| **Análisis** | Básico | Estándar | Avanzado | Personalizado |
| **Acceso API** | ❌ | ❌ | ✅ | ✅ |
| **Soporte** | Email | Prioritario | Teléfono | Dedicado |
| **Dominio Personalizado** | ❌ | ❌ | ✅ | ✅ |
| **Marca Blanca** | ❌ | ❌ | ❌ | ✅ |

---

## Estrategia de Comercialización

### Perfil del Cliente Objetivo
- Negocios pequeños de alquiler de vehículos (10-50 unidades)
- Actualmente usando hojas de cálculo o software obsoleto
- Basados en México y Latinoamérica (mercado inicial)
- Ingresos: $1.7M - $34M MXN/año
- Problema: Procesos manuales, sin reservas en línea, dobles reservaciones

### Canales de Adquisición
1. **SEO/Contenido** — "software de alquiler de autos", "gestión de flota pequeño negocio"
2. **Google Ads** — Palabras clave de negocios de alquiler
3. **Foros de la Industria** — Comunidades de asociaciones de alquiler
4. **Alcance Directo** — LinkedIn, correo frío
5. **Programa de Referidos** — 1 mes gratis por referido

### Embudo de Conversión
```
Página de Destino → Prueba Gratis (14 días) → Onboarding → Suscripción Paga
     ↓                    ↓                       ↓              ↓
   100%                  20%                     60%            70%
              (de visitantes)      (de inicios de prueba) (de onboarded)
```

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación |
|--------|---------|--------------|------------|
| Baja adopción inicial | Alto | Media | Prueba gratis, marketing de contenido |
| Alto abandono | Alto | Media | Soporte de onboarding, características adhesivas |
| Competencia | Medio | Baja | Enfoque en PYMES, mejor UX, menor precio |
| Problemas de escalado | Medio | Baja | Arquitectura nativa de la nube |
| Brecha de seguridad | Alto | Baja | Cumplimiento SOC 2, encriptación |
| Fallos de pago | Medio | Media | Emails de dunning, período de gracia |

---

## Hoja de Ruta de Desarrollo

| Época | Enfoque | Duración | Entregables Clave |
|-------|---------|----------|-------------------|
| 1 | MVP | 4 semanas | Core multi-inquilino, flota, reservaciones |
| 2 | Monetización | 4 semanas | Reservas en línea, pagos, facturación Stripe |
| 3 | Adhesión | 4 semanas | GPS, mantenimiento, análisis |
| 4 | Móvil | 4 semanas | App iOS/Android |
| 5 | Escala | Continuo | Herramientas admin, API, marca blanca |

---

## Criterios de Éxito

### Lanzamiento MVP (Época 1-2)
- [ ] Arquitectura multi-inquilino funcionando
- [ ] 10 clientes beta registrados
- [ ] Facturación Stripe integrada
- [ ] 99% de disponibilidad lograda

### Product-Market Fit (Mes 6)
- [ ] 50 clientes pagando
- [ ] <5% abandono mensual
- [ ] LTV > 3x CAC
- [ ] Puntuación NPS > 40

### Fase de Crecimiento (Mes 12)
- [ ] 100+ clientes pagando
- [ ] $340,000+ MXN MRR
- [ ] App móvil lanzada
- [ ] Rentabilidad operativa

---

## Historial del Documento

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Dic 2025 | Carta inicial SaaS |
