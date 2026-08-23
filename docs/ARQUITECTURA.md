# Arquitectura recomendada

## Principios

- Monolito modular Django: despliegue sencillo y limites de dominio claros.
- Aislamiento multi-sucursal: toda consulta operativa se filtra por la farmacia activa y el backend valida `UsuarioFarmacia`.
- Inventario inmutable por eventos: el stock solo cambia en servicios atomicos que bloquean filas con `select_for_update()` y crean `MovimientoInventario`.
- Borrado logico para maestros; documentos comerciales se anulan y generan reversos.
- API REST bajo `/api/v1/`; templates Bootstrap consumen los mismos servicios de dominio.

## Aplicaciones

`core` (bases y utilidades), `usuarios`, `farmacias`, `categorias`, `laboratorios`, `medicamentos`, `proveedores`, `clientes`, `inventario`, `lotes`, `compras`, `ventas`, `cajas`, `transferencias`, `reportes`, `auditoria`, `notificaciones` y `configuracion`.

Cada aplicacion evolucionara con `models`, `services`, `selectors`, `validators`, `permissions`, `forms`, `views`, `api`, `urls`, `signals` y `tests` solo cuando los necesite.

## Modelo de datos final

- `Usuario` 1--N `UsuarioFarmacia` N--1 `Farmacia`. La asignacion contiene rol, estado y fecha.
- `Categoria` y `Laboratorio` 1--N `Medicamento`.
- `Farmacia` 1--N `InventarioFarmacia` N--1 `Medicamento`; unicidad por farmacia y medicamento.
- `Medicamento` + `Farmacia` 1--N `Lote`; un lote referencia opcionalmente a `Proveedor`.
- `MovimientoInventario` referencia farmacia, medicamento, lote, usuario y documento origen. Es la fuente del Kardex; no se edita ni elimina.
- `Proveedor` 1--N `Compra` 1--N `DetalleCompra`; cada detalle origina lotes y movimientos dentro de una unica transaccion.
- `Cliente` y `Farmacia` 1--N `Venta` 1--N `DetalleVenta`; `DetalleVentaLote` permite consumo FEFO de varios lotes.
- `Caja` 1--N `MovimientoCaja`; ventas y movimientos manuales mantienen referencias auditables.
- `Transferencia` 1--N `DetalleTransferencia`; envio descuenta origen y recepcion aumenta destino, nunca antes.
- `ConteoFisico` 1--N `DetalleConteo`; la aprobacion crea `AjusteInventario` y movimientos.
- `HistorialPrecio`, `Notificacion`, `AuditLog` y `ConfiguracionFarmacia` conservan contexto de farmacia y responsable.

Restricciones clave: barcode global unico; documentos numerados por farmacia; cantidades/costos no negativos; origen distinto de destino; indices compuestos por farmacia y fecha; `PROTECT` en documentos historicos.

## Roles iniciales

- Superadministrador: acceso global y configuracion de plataforma.
- Administrador: gestion completa de farmacias asignadas.
- Farmaceutico: medicamentos, lotes, dispensacion e inventario.
- Encargado de inventario: catalogo, compras, movimientos, conteos y transferencias.
- Cajero/Vendedor: POS, clientes y caja.
- Consulta: lectura y reportes autorizados.

Los roles son perfiles iniciales. Los permisos efectivos usan permisos Django y se comprueban junto con la membresia de farmacia en cada endpoint/servicio.

## Flujo seguro de stock

Dentro de `transaction.atomic()`: validar permiso y farmacia; bloquear inventario/lotes; validar cantidad y vencimiento; elegir lotes FEFO; crear documento; actualizar cantidades con expresiones seguras; crear movimientos; registrar auditoria. Cualquier fallo revierte todo.

## Variables de entorno

Definidas en `.env.example`: settings, secreto, debug, hosts/CSRF, base de datos, zona horaria, OAuth Google, correo, Redis futuro y sesion. `.env` esta excluido del control de versiones.

## Fases siguientes

1. Migraciones y autenticacion/membresia con middleware de farmacia activa.
2. CRUD de catalogo e inventario, permisos y tests de aislamiento.
3. Compras y servicio atomico de entradas/Kardex.
4. POS, ventas FEFO, clientes y caja.
5. Transferencias, ajustes, conteos y vencimientos.
6. Dashboard, reportes, notificaciones, auditoria y tareas.
7. Integracion del design system cuando exista el archivo o enlace de Figma.
8. Pruebas integrales, optimizacion, seed y despliegue.
