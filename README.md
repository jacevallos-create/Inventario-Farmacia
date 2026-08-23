# Sistema Integral de Gestión Farmacéutica

Aplicación Django 5.2 con frontend React/Vite, inventario por farmacia y API REST.

## Desarrollo local

Requiere Python 3.12 o 3.13 y Node.js 20 o superior. Si un entorno virtual fue copiado desde otro equipo, elimínelo y créelo nuevamente; los entornos virtuales no son portables.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Para usar SQLite localmente, deje `DATABASE_URL=` vacío en `.env`. Después:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
python manage.py migrate
python manage.py seed
python manage.py check
python manage.py runserver
```

Abra `http://127.0.0.1:8000/`. El usuario demostrativo creado por `seed` es `admin@demo.local` / `AdminDemo2026!`; cambie la contraseña en cualquier entorno publicado.

## Supabase (PostgreSQL)

1. Cree un proyecto en Supabase.
2. Abra **Connect** y elija **Transaction pooler**. Es la opción más compatible con Render cuando no hay IPv6 disponible.
3. Copie la URI y reemplace `[YOUR-PASSWORD]` por la contraseña de la base. Debe tener esta forma:

   ```text
   postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres?sslmode=require
   ```

4. Guarde la URI completa como `DATABASE_URL`. No la suba a GitHub.
5. Para probar Supabase desde su equipo, ponga temporalmente esa URI en `.env` y ejecute `python manage.py migrate` y `python manage.py check`.

Esto cambia la base de datos usada por Django, no el sistema de archivos. Los archivos cargados en `media/` no son persistentes en Render; si la aplicación empieza a guardar imágenes o documentos, conviene conectarlos por separado a Supabase Storage o a otro almacenamiento de objetos.

## Subir a GitHub

Ejecute los comandos desde esta carpeta (no desde `C:\Users\crist`):

```powershell
git init
git add .
git commit -m "Preparar aplicacion para Supabase y Render"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Si `origin` ya existe, use:

```powershell
git remote set-url origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Antes del commit, `git status` no debe mostrar `.env`, `.venv` ni `db.sqlite3`.

## Desplegar en Render

El archivo `render.yaml` contiene el build, el arranque, las migraciones y el health check.

1. En Render elija **New > Blueprint** y conecte el repositorio de GitHub.
2. Seleccione el `render.yaml` de este repositorio.
3. Cuando Render solicite `DATABASE_URL`, pegue la URI del Transaction pooler de Supabase. No use la API URL `https://...supabase.co` ni las claves `anon` o `service_role`: Django necesita la URI PostgreSQL.
4. Cree el servicio. El build instala Python y Node, compila React, ejecuta `collectstatic` y aplica las migraciones.
5. Compruebe `https://SU-SERVICIO.onrender.com/api/v1/health/` y luego la raíz.
6. Cree el administrador desde **Shell** de Render con `python manage.py createsuperuser`, o ejecute `python manage.py seed` solo si desea cargar los datos demostrativos.

Para despliegue manual sin Blueprint, use:

- Build command: `bash build.sh`
- Start command: `gunicorn config.wsgi:application`
- Variables obligatorias: `DJANGO_SETTINGS_MODULE=config.settings.production`, `DJANGO_SECRET_KEY`, `DATABASE_URL` y `TIME_ZONE=America/Guayaquil`.

## Verificación

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
npm.cmd --prefix frontend run build
```
