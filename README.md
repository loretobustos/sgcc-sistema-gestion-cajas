# SGCC - Sistema de Gestión y Control de Cajeros

Sistema web desarrollado en **Django** para la administración en tiempo real, control de turnos, monitoreo de estado por semáforo y auditoría de hasta 70 puestos de caja en entornos operativos.

---

## 🚀 Características Principales

* **Autenticación de Jefatura:** Acceso administrativo validado bajo el rango numérico estricto $[1120, 1140]$.
* **Gestión de Inventario Finito (01 al 70):** Alta, edición y control de puestos de caja con validación contra asignaciones duplicadas.
* **Monitoreo en Tiempo Real (Semáforo Operativo):**
  * 🟢 **Activo:** Puesto operando con normalidad.
  * 🟡 **Colación / Pausa:** Turno temporalmente pausado.
  * 🔴 **Inactivo / Cerrado:** Puesto liberado o fuera de servicio.
* **Diferenciación de Personal:** Clasificación y filtrado entre personal interno y personal de empresas externas (C.E).
* **Auditoría y Reportería:** Bitácora inmutable de eventos administrativos y exportación de métricas operativas a formato **CSV**.
* **Cierre General de Jornada:** Funcionalidad global de cierre y liberación masiva de sala.

---

## 🛠️ Tecnologías y Stack Utilizado

* **Backend:** Python 3.13, Django 6.1
* **Base de Datos:** SQLite (Entorno de desarrollo local)
* **Frontend / UI:** Bootstrap 5, HTML5, CSS3, Plantillas nativas de Django
* **Gestión y Metodología:** Git, GitHub, Jira (Scrum-Kanban)

---

## ⚙️ Instrucciones de Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/TU_USUARIO/sgcc-sistema-gestion-cajas.git](https://github.com/TU_USUARIO/sgcc-sistema-gestion-cajas.git)
   cd sgcc-sistema-gestion-cajas