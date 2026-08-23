import { useMemo, useState, useEffect } from "react";
import {
  AlertTriangle,
  ArrowLeftRight,
  BarChart3,
  Bell,
  Building2,
  CheckCircle2,
  ClipboardList,
  ChevronDown,
  Download,
  Edit3,
  Eye,
  EyeOff,
  FileSpreadsheet,
  FlaskConical,
  LayoutDashboard,
  LogOut,
  Menu,
  Package,
  Plus,
  RefreshCw,
  ScanLine,
  Search,
  ShieldCheck,
  ShoppingCart,
  Trash2,
  Truck,
  Users,
  Wallet,
  X,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const money = (n) =>
  new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  }).format(n || 0);
const csrfToken = () =>
  document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1] || "";

const deleteRemote = async (resource, identifier, branch = "") => {
  const query = branch ? `?branch=${encodeURIComponent(branch)}` : "";
  const response = await fetch(
    `/api/v1/state/${resource}/${encodeURIComponent(identifier)}/${query}`,
    {
      method: "DELETE",
      credentials: "same-origin",
      headers: { "X-CSRFToken": csrfToken() },
    },
  );
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || "No se pudo eliminar el registro.");
  }
};
const defaultBranches = [
  { id: "central", name: "Farmacia Central", address: "Av. Central 123" },
  { id: "norte", name: "Sucursal Norte", address: "Calle 80 #24-16" },
  { id: "sur", name: "Sucursal Sur", address: "Carrera 45 #12-08" },
];
const defaultSuppliers = [
  {
    id: 1,
    name: "Distribuciones Genfar",
    taxId: "900123456-1",
    contact: "Carlos Ruiz",
    phone: "310 222 1045",
    email: "ventas@genfar.com",
    city: "Bogotá",
    active: true,
  },
  {
    id: 2,
    name: "Tecnoquímicas S.A.",
    taxId: "890900010-2",
    contact: "Laura Gómez",
    phone: "300 555 0188",
    email: "pedidos@tq.com.co",
    city: "Cali",
    active: true,
  },
  {
    id: 3,
    name: "Sanofi Colombia",
    taxId: "860020570-1",
    contact: "Diana Pérez",
    phone: "315 480 2271",
    email: "distribucion@sanofi.com",
    city: "Bogotá",
    active: true,
  },
];
const defaultUsers = [
  {
    id: 1,
    name: "Administrador PharmaSys",
    email: "admin@pharmasys.com",
    password: "Admin2026!",
    role: "ADMIN",
    branchIds: ["central", "norte", "sur"],
    active: true,
  },
  {
    id: 2,
    name: "Encargado Central",
    email: "inventario.central@pharmasys.com",
    password: "Inventario2026!",
    role: "INVENTARIO",
    branchIds: ["central"],
    active: true,
  },
];
const labs = [
  "Bayer",
  "Pfizer",
  "Genfar",
  "Roche",
  "Sanofi",
  "Tecnoquímicas",
  "MK",
];
const presentations = [
  "Tabletas",
  "Cajas",
  "Jarabe",
  "Blíster",
  "Ampollas",
  "Crema",
  "Cápsulas",
];
const categories = [
  "Analgésicos y antipiréticos",
  "Antibióticos",
  "Antiinflamatorios",
  "Antialérgicos",
  "Cardiovasculares",
  "Gastrointestinales",
  "Respiratorios",
  "Antidiabéticos",
  "Dermatológicos",
  "Vitaminas y suplementos",
  "Sistema nervioso",
  "Salud sexual y reproductiva",
  "Oftálmicos",
  "Pediátricos",
  "Primeros auxilios",
  "Dispositivos médicos",
  "Cuidado personal",
  "Otros",
];
const starter = {
  central: [
    {
      id: 1,
      name: "Acetaminofén 500 mg",
      barcode: "7702057001012",
      sku: "MED-001",
      lab: "Genfar",
      presentation: "Tabletas",
      buyPrice: 4200,
      sellPrice: 5460,
      margin: 30,
      min: 15,
      stock: 84,
    },
    {
      id: 2,
      name: "Amoxicilina 500 mg",
      barcode: "7702057001142",
      sku: "MED-014",
      lab: "Pfizer",
      presentation: "Cápsulas",
      buyPrice: 12800,
      sellPrice: 16640,
      margin: 30,
      min: 12,
      stock: 8,
    },
    {
      id: 3,
      name: "Insulina glargina",
      barcode: "7702057001234",
      sku: "MED-023",
      lab: "Sanofi",
      presentation: "Ampollas",
      buyPrice: 53000,
      sellPrice: 68900,
      margin: 30,
      min: 8,
      stock: 0,
    },
    {
      id: 4,
      name: "Loratadina 10 mg",
      barcode: "7702057001102",
      sku: "MED-102",
      lab: "MK",
      presentation: "Tabletas",
      buyPrice: 4800,
      sellPrice: 6240,
      margin: 30,
      min: 15,
      stock: 68,
    },
    {
      id: 5,
      name: "Omeprazol 20 mg",
      barcode: "7702057001028",
      sku: "MED-028",
      lab: "Genfar",
      presentation: "Cápsulas",
      buyPrice: 9500,
      sellPrice: 12350,
      margin: 30,
      min: 10,
      stock: 19,
    },
  ],
  norte: [
    {
      id: 6,
      name: "Ibuprofeno 400 mg",
      barcode: "7702057001041",
      sku: "MED-041",
      lab: "Bayer",
      presentation: "Tabletas",
      buyPrice: 6000,
      sellPrice: 7800,
      margin: 30,
      min: 12,
      stock: 26,
    },
  ],
  sur: [],
};
const loadInventories = () => {
  const saved = JSON.parse(
    localStorage.getItem("pharma-inventories") || "null",
  );
  if (!saved) return starter;
  return Object.fromEntries(
    Object.entries(saved).map(([branch, items]) => [
      branch,
      items.map((p) => ({
        ...p,
        category: p.category || "Otros",
        lab: p.lab || p.supplier || "Genfar",
        presentation: p.presentation || "Tabletas",
        buyPrice: Number(p.buyPrice ?? p.price ?? 0),
        margin: Number(p.margin ?? 30),
        sellPrice: Number(
          p.sellPrice ?? Math.round(Number(p.price || 0) * 1.3),
        ),
        min: Number(p.min || 0),
        stock: Number(p.stock || 0),
      })),
    ]),
  );
};
const nav = [
  ["Dashboard", LayoutDashboard],
  ["Inventario", Package],
  ["Punto de Venta (POS)", ShoppingCart],
  ["Sucursales", Building2],
  ["Proveedores", Truck],
  ["Compras", ClipboardList],
  ["Transferencias", ArrowLeftRight],
  ["Caja", Wallet],
  ["Usuarios y Accesos", Users],
  ["Reportes", BarChart3],
];
const trend = [
  { m: "Mar", v: 980 },
  { m: "Abr", v: 1120 },
  { m: "May", v: 1060 },
  { m: "Jun", v: 1280 },
  { m: "Jul", v: 1210 },
  { m: "Ago", v: 1390 },
];
const getStatus = (p) =>
  p.stock === 0
    ? ["Agotado", "danger"]
    : p.stock <= p.min
      ? ["Stock Crítico", "warning"]
      : ["En Stock", "success"];

const exportExcel = async ({ filename, sheetName, columns, rows }) => {
  const { default: ExcelJS } = await import("exceljs");
  const workbook = new ExcelJS.Workbook();
  workbook.creator = "PharmaSys";
  workbook.created = new Date();
  const sheet = workbook.addWorksheet(sheetName, {
    views: [{ state: "frozen", ySplit: 1 }],
  });
  sheet.columns = columns.map((column) => ({
    header: column.header,
    key: column.key,
    width: column.width || 20,
  }));
  rows.forEach((row) => sheet.addRow(row));
  const header = sheet.getRow(1);
  header.height = 24;
  header.font = { bold: true, color: { argb: "FFFFFFFF" } };
  header.fill = {
    type: "pattern",
    pattern: "solid",
    fgColor: { argb: "FF4F46E5" },
  };
  header.alignment = { vertical: "middle" };
  sheet.autoFilter = {
    from: { row: 1, column: 1 },
    to: { row: 1, column: columns.length },
  };
  sheet.eachRow((row, index) => {
    if (index > 1 && index % 2 === 0)
      row.fill = {
        type: "pattern",
        pattern: "solid",
        fgColor: { argb: "FFF5F7FB" },
      };
  });
  const buffer = await workbook.xlsx.writeBuffer(),
    url = URL.createObjectURL(
      new Blob([buffer], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      }),
    ),
    link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
};

function ConfirmDialog({
  icon: Icon = ShieldCheck,
  eyebrow = "CONFIRMACIÓN",
  title,
  message,
  confirmLabel = "Confirmar",
  tone = "primary",
  busy = false,
  onConfirm,
  onClose,
}) {
  return (
    <div
      className="modal-backdrop confirm-backdrop"
      role="presentation"
      onMouseDown={(e) => e.target === e.currentTarget && !busy && onClose()}
    >
      <section
        className="confirm-dialog"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
      >
        <button
          className="confirm-close"
          onClick={onClose}
          disabled={busy}
          aria-label="Cerrar"
        >
          <X />
        </button>
        <span className={`confirm-icon ${tone}`}>
          <Icon />
        </span>
        <p className="eyebrow">{eyebrow}</p>
        <h2 id="confirm-title">{title}</h2>
        <p className="confirm-message">{message}</p>
        <div className="confirm-actions">
          <button
            className="button secondary"
            onClick={onClose}
            disabled={busy}
          >
            Cancelar
          </button>
          <button
            className={`button ${tone === "danger" ? "danger" : "primary"}`}
            onClick={onConfirm}
            disabled={busy}
          >
            {busy ? "Preparando…" : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}

function SuccessToast({ message }) {
  return (
    <div className="success-toast" role="status">
      <span>
        <CheckCircle2 />
      </span>
      <div>
        <b>Operación completada</b>
        <small>{message}</small>
      </div>
    </div>
  );
}

function useDeleteConfirmation() {
  const [pending, setPending] = useState(null);
  const askDelete = ({ title, message }) =>
    new Promise((resolve) => setPending({ title, message, resolve }));
  const finish = (accepted) => {
    pending?.resolve(accepted);
    setPending(null);
  };
  const deleteDialog = pending ? (
    <ConfirmDialog
      icon={Trash2}
      eyebrow="CONFIRMAR ELIMINACIÓN"
      title={pending.title}
      message={pending.message}
      confirmLabel="Sí, eliminar"
      tone="danger"
      onClose={() => finish(false)}
      onConfirm={() => finish(true)}
    />
  ) : null;
  return [askDelete, deleteDialog];
}

function useActionConfirmation() {
  const [pending, setPending] = useState(null);
  const askConfirm = (options) =>
    new Promise((resolve) => setPending({ ...options, resolve }));
  const finish = (accepted) => {
    pending?.resolve(accepted);
    setPending(null);
  };
  const dialog = pending ? (
    <ConfirmDialog
      icon={pending.icon || CheckCircle2}
      eyebrow={pending.eyebrow || "CONFIRMAR OPERACIÓN"}
      title={pending.title}
      message={pending.message}
      confirmLabel={pending.confirmLabel || "Confirmar"}
      tone={pending.tone || "primary"}
      onClose={() => finish(false)}
      onConfirm={() => finish(true)}
    />
  ) : null;
  return [askConfirm, dialog];
}

function Login({ onLogin }) {
  return (
    <main className="login-shell">
      <section className="login-brand">
        <div className="brand">
          <span>
            <FlaskConical size={23} />
          </span>
          PharmaSys
        </div>
        <div>
          <p className="eyebrow light">INVENTARIO MULTI-SUCURSAL</p>
          <h1>
            Medicamentos disponibles.
            <br />
            Decisiones más seguras.
          </h1>
          <p>
            Controla existencias, precios y alertas de todas tus farmacias desde
            un solo lugar.
          </p>
          <div className="login-stats">
            <div>
              <b>3</b>
              <small>Sucursales</small>
            </div>
            <div>
              <b>24/7</b>
              <small>Monitoreo</small>
            </div>
            <div>
              <b>100%</b>
              <small>Trazabilidad</small>
            </div>
          </div>
        </div>
        <small>Gestión farmacéutica segura y centralizada</small>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <div className="brand mobile">
            <span>
              <FlaskConical size={21} />
            </span>
            PharmaSys
          </div>
          <p className="eyebrow">BIENVENIDO</p>
          <h2>Inicia sesión en tu cuenta</h2>
          <p>Usa tu cuenta corporativa de Google para acceder al sistema.</p>
          <button className="google-button" onClick={onLogin}>
            <img
              src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
              alt=""
            />
            Continuar con Google
          </button>
          <div className="security-note">
            Acceso protegido mediante Google OAuth 2.0
          </div>
          <p className="legal">
            Al continuar, aceptas nuestros <a>Términos de servicio</a> y la{" "}
            <a>Política de privacidad</a>.
          </p>
        </div>
      </section>
    </main>
  );
}

function PharmaLogin({ onLogin, branches }) {
  const [branchId, setBranchId] = useState(branches[0]?.id || "central");
  return (
    <main className="login-shell">
      <section className="login-brand">
        <div className="brand">
          <span>
            <FlaskConical size={23} />
          </span>
          PharmaSys
        </div>
        <div>
          <p className="eyebrow light">GESTIÓN FARMACÉUTICA MULTI-SUCURSAL</p>
          <h1>
            Una operación clara.
            <br />
            Todas tus farmacias.
          </h1>
          <p>
            Inventario, ventas, proveedores y reportes en un solo espacio de
            trabajo seguro.
          </p>
          <div className="login-stats">
            <div>
              <b>{branches.length}</b>
              <small>Sucursales</small>
            </div>
            <div>
              <b>24/7</b>
              <small>Monitoreo</small>
            </div>
            <div>
              <b>100%</b>
              <small>Trazabilidad</small>
            </div>
          </div>
        </div>
        <small>PharmaSys · Gestión segura y centralizada</small>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <div className="brand mobile">
            <span>
              <FlaskConical size={21} />
            </span>
            PharmaSys
          </div>
          <p className="eyebrow">BIENVENIDO</p>
          <h2>Accede a PharmaSys</h2>
          <p>
            Selecciona tu sucursal inicial y continúa con tu cuenta corporativa.
          </p>
          <label className="login-branch">
            Sucursal
            <select
              value={branchId}
              onChange={(e) => setBranchId(e.target.value)}
            >
              {branches
                .filter((b) => b.active !== false)
                .map((b) => (
                  <option value={b.id} key={b.id}>
                    {b.name}
                  </option>
                ))}
            </select>
          </label>
          <button className="google-button" onClick={() => onLogin(branchId)}>
            <img
              src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
              alt=""
            />
            Continuar con Google
          </button>
          <div className="security-note">
            Acceso protegido mediante Google OAuth 2.0
          </div>
          <p className="legal">
            Al continuar, aceptas nuestros <a>Términos de servicio</a> y la{" "}
            <a>Política de privacidad</a>.
          </p>
        </div>
      </section>
    </main>
  );
}

function CredentialLogin({ onLogin }) {
  const [email, setEmail] = useState(""),
    [password, setPassword] = useState(""),
    [show, setShow] = useState(false),
    [error, setError] = useState(""),
    [loading, setLoading] = useState(false);
  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];
    try {
      const response = await fetch("/api/v1/auth/login/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({ email: email.trim(), password }),
      });
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail || "No fue posible iniciar sesión.");
      onLogin(data.user);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <main className="login-shell">
      <section className="login-brand">
        <div className="brand">
          <span>
            <FlaskConical size={23} />
          </span>
          PharmaSys
        </div>
        <div>
          <p className="eyebrow light">GESTIÓN FARMACÉUTICA MULTI-SUCURSAL</p>
          <h1>
            Control por sede.
            <br />
            Acceso por responsabilidades.
          </h1>
          <p>
            Administra inventarios, colaboradores y reportes con permisos
            específicos para cada farmacia.
          </p>
          <div className="login-stats">
            <div>
              <b>Seguro</b>
              <small>Roles y permisos</small>
            </div>
            <div>
              <b>24/7</b>
              <small>Monitoreo</small>
            </div>
            <div>
              <b>100%</b>
              <small>Trazabilidad</small>
            </div>
          </div>
        </div>
        <small>PharmaSys · Gestión segura y centralizada</small>
      </section>
      <section className="login-panel">
        <div className="login-card">
          <div className="brand mobile">
            <span>
              <FlaskConical size={21} />
            </span>
            PharmaSys
          </div>
          <p className="eyebrow">ACCESO SEGURO</p>
          <h2>Inicia sesión</h2>
          <p>Ingresa con las credenciales asignadas por el administrador.</p>
          {error && <div className="login-error">{error}</div>}
          <form className="credential-form" onSubmit={submit}>
            <label>
              Correo electrónico
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </label>
            <label>
              Contraseña
              <div className="password-field">
                <input
                  type={show ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  required
                />
                <button type="button" onClick={() => setShow(!show)}>
                  {show ? <EyeOff /> : <Eye />}
                </button>
              </div>
            </label>
            <div className="login-options">
              <label>
                <input type="checkbox" /> Recordarme
              </label>
            </div>
            <button className="button primary login-submit" disabled={loading}>
              {loading ? "Validando…" : "Iniciar sesión"}
            </button>
          </form>
          <div className="login-divider">
            <span>O continúa con</span>
          </div>
          <button
            className="google-button compact"
            onClick={() =>
              window.location.assign("/accounts/google/login/?process=login")
            }
          >
            <img
              src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
              alt=""
            />
            Continuar con Google
          </button>
          <p className="demo-access">Admin: admin@pharmasys.com · Admin2026!</p>
          <p className="legal">
            Al continuar, aceptas los <a>Términos</a> y la{" "}
            <a>Política de privacidad</a>.
          </p>
        </div>
      </section>
    </main>
  );
}

function MedicineModal({ medicine, onClose, onSave }) {
  const [form, setForm] = useState(
    medicine || {
      name: "",
      category: "Analgésicos y antipiréticos",
      barcode: "",
      sku: "",
      lab: "Genfar",
      presentation: "Tabletas",
      buyPrice: "",
      margin: 30,
      min: 10,
      stock: 0,
    },
  );
  const [barcodeEnabled, setBarcodeEnabled] = useState(
    Boolean(medicine?.barcode),
  );
  const sellPrice = Math.round(
    Number(form.buyPrice || 0) * (1 + Number(form.margin || 0) / 100),
  );
  const change = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <section className="modal-card">
        <header>
          <div>
            <p className="eyebrow">INVENTARIO FARMACÉUTICO</p>
            <h2>{medicine ? "Editar medicamento" : "Nuevo medicamento"}</h2>
          </div>
          <button className="icon-button" onClick={onClose}>
            <X />
          </button>
        </header>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSave({
              ...form,
              buyPrice: Number(form.buyPrice),
              sellPrice,
              margin: Number(form.margin),
              min: Number(form.min),
              stock: Number(form.stock),
              barcode: barcodeEnabled ? form.barcode : "",
            });
          }}
        >
          <div className="form-grid">
            <label className="wide">
              Nombre del medicamento
              <input
                name="name"
                value={form.name}
                onChange={change}
                placeholder="Ej. Acetaminofén 500 mg"
                required
              />
            </label>
            <label>
              Categoría terapéutica
              <select name="category" value={form.category} onChange={change}>
                {categories.map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
            <label>
              Código interno / SKU
              <input
                name="sku"
                value={form.sku}
                onChange={change}
                placeholder="MED-001"
                required
              />
            </label>
            <label>
              Código de barras
              <div className="input-action">
                <input
                  name="barcode"
                  value={form.barcode}
                  onChange={change}
                  disabled={!barcodeEnabled}
                  placeholder={
                    barcodeEnabled
                      ? "Escanea o escribe el código"
                      : "Código deshabilitado"
                  }
                />
                <button
                  type="button"
                  title="Simular escaneo"
                  disabled={!barcodeEnabled}
                  onClick={() =>
                    setForm({ ...form, barcode: String(Date.now()).slice(-13) })
                  }
                >
                  <ScanLine size={18} />
                </button>
              </div>
              <span className="check-row">
                <input
                  type="checkbox"
                  checked={barcodeEnabled}
                  onChange={(e) => setBarcodeEnabled(e.target.checked)}
                />{" "}
                Habilitar código de barras
              </span>
            </label>
            <label>
              Laboratorio
              <select name="lab" value={form.lab} onChange={change}>
                {labs.map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
            <label>
              Presentación
              <select
                name="presentation"
                value={form.presentation}
                onChange={change}
              >
                {presentations.map((x) => (
                  <option key={x}>{x}</option>
                ))}
              </select>
            </label>
            <label>
              Precio de compra ($)
              <input
                type="number"
                min="0"
                name="buyPrice"
                value={form.buyPrice}
                onChange={change}
                required
              />
            </label>
            <label>
              Margen de venta (%)
              <input
                type="number"
                min="0"
                name="margin"
                value={form.margin}
                onChange={change}
                required
              />
            </label>
            <label>
              Precio de venta calculado
              <div className="calculated">
                {money(sellPrice)}
                <small>Compra + {form.margin || 0}%</small>
              </div>
            </label>
            <label>
              Stock mínimo permanente
              <input
                type="number"
                min="0"
                name="min"
                value={form.min}
                onChange={change}
                required
              />
            </label>
            <label>
              Stock actual
              <input
                type="number"
                min="0"
                name="stock"
                value={form.stock}
                onChange={change}
                required
              />
            </label>
          </div>
          <footer>
            <button
              type="button"
              className="button secondary"
              onClick={onClose}
            >
              Cancelar
            </button>
            <button className="button primary">
              {medicine ? "Guardar cambios" : "Agregar medicamento"}
            </button>
          </footer>
        </form>
      </section>
    </div>
  );
}

function Sidebar({ active, setActive, open, setOpen, user }) {
  const visible =
    user.role === "ADMIN"
      ? nav
      : nav.filter(([label]) =>
          ["Dashboard", "Inventario", "Punto de Venta (POS)"].includes(label),
        );
  return (
    <>
      <div
        className={`mobile-overlay ${open ? "show" : ""}`}
        onClick={() => setOpen(false)}
      />
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="brand">
          <span>
            <FlaskConical size={22} />
          </span>
          PharmaSys
          <button onClick={() => setOpen(false)}>
            <X />
          </button>
        </div>
        <nav>
          {visible.map(([label, Icon]) => (
            <button
              key={label}
              className={active === label ? "active" : ""}
              onClick={() => {
                setActive(label);
                setOpen(false);
              }}
            >
              <Icon size={19} />
              {label}
            </button>
          ))}
        </nav>
        <div className="help">
          <Users size={20} />
          <b>
            {user.role === "ADMIN"
              ? "Acceso administrador"
              : "Acceso de inventario"}
          </b>
          <p>
            {user.role === "ADMIN"
              ? "Gestiona todas las sedes y sus usuarios."
              : "Solo puedes operar la sucursal asignada."}
          </p>
        </div>
      </aside>
    </>
  );
}

function Inventory({ items, setItems, branchId, onAdd, initialQuery = "" }) {
  const [query, setQuery] = useState(initialQuery),
    [category, setCategory] = useState("Todas"),
    [lab, setLab] = useState("Todos"),
    [presentation, setPresentation] = useState("Todas"),
    [alert, setAlert] = useState("Todos"),
    [showCode, setShowCode] = useState(true),
    [editing, setEditing] = useState(null);
  const [askDelete, deleteDialog] = useDeleteConfirmation();
  useEffect(() => setQuery(initialQuery), [initialQuery]);
  const rows = useMemo(
    () =>
      items.filter(
        (p) =>
          `${p.name} ${p.sku} ${p.barcode}`
            .toLowerCase()
            .includes(query.toLowerCase()) &&
          (category === "Todas" || p.category === category) &&
          (lab === "Todos" || p.lab === lab) &&
          (presentation === "Todas" || p.presentation === presentation) &&
          (alert === "Todos" || getStatus(p)[0] === alert),
      ),
    [items, query, category, lab, presentation, alert],
  );
  const save = (m) => {
    setItems(items.map((x) => (x.id === m.id ? m : x)));
    setEditing(null);
  };
  const remove = async (p) => {
    const accepted = await askDelete({
      title: `¿Eliminar ${p.name}?`,
      message:
        "El medicamento se quitará del inventario de esta sucursal. Esta acción no se puede deshacer.",
    });
    if (accepted) {
      try {
        await deleteRemote("inventory", p.id, branchId);
        setItems(items.filter((x) => x.id !== p.id));
      } catch (error) {
        alert(error.message);
      }
    }
  };
  const restock = (p) => {
    const amount = Number(prompt(`Cantidad para reabastecer ${p.name}:`, 10));
    if (amount > 0)
      setItems(
        items.map((x) =>
          x.id === p.id ? { ...x, stock: x.stock + amount } : x,
        ),
      );
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">CONTROL DE EXISTENCIAS</p>
          <h1>Inventario de medicamentos</h1>
          <p>{rows.length} medicamentos en la sucursal seleccionada</p>
        </div>
        <button className="button primary" onClick={onAdd}>
          <Plus size={18} />
          Nuevo medicamento
        </button>
      </section>
      <section className="filter-card">
        <div className="search-box">
          <Search size={18} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar por nombre, SKU o código de barras"
          />
        </div>
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          <option>Todas</option>
          {categories.map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select value={lab} onChange={(e) => setLab(e.target.value)}>
          <option>Todos</option>
          {labs.map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select
          value={presentation}
          onChange={(e) => setPresentation(e.target.value)}
        >
          <option>Todas</option>
          {presentations.map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
        <select value={alert} onChange={(e) => setAlert(e.target.value)}>
          <option>Todos</option>
          <option>En Stock</option>
          <option>Stock Crítico</option>
          <option>Agotado</option>
        </select>
        <button className="button ghost" onClick={() => setShowCode(!showCode)}>
          {showCode ? <EyeOff size={17} /> : <Eye size={17} />}Código
        </button>
      </section>
      <section className="table-card">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {showCode && <th>Código / Barcode</th>}
                <th>Medicamento</th>
                <th>Laboratorio</th>
                <th>Precio compra</th>
                <th>Precio venta</th>
                <th>Stock</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((p) => {
                const [label, tone] = getStatus(p),
                  percent = Math.min(
                    100,
                    (p.stock / Math.max(p.min * 3, 1)) * 100,
                  );
                return (
                  <tr key={p.id}>
                    {showCode && (
                      <td>
                        <b>{p.sku}</b>
                        <small>{p.barcode || "Sin barcode"}</small>
                      </td>
                    )}
                    <td>
                      <div className="medicine">
                        <span>
                          <Package size={19} />
                        </span>
                        <div>
                          <b>{p.name}</b>
                          <small>{p.presentation}</small>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span className="lab-badge">{p.lab}</span>
                    </td>
                    <td>{money(p.buyPrice)}</td>
                    <td>
                      <b>{money(p.sellPrice)}</b>
                    </td>
                    <td>
                      <div className="stock-number">
                        <b>{p.stock}</b>
                        <small>Mín. {p.min}</small>
                      </div>
                      <div className={`stock-bar ${tone}`}>
                        <i style={{ width: `${percent}%` }} />
                      </div>
                    </td>
                    <td>
                      <span className={`status ${tone}`}>{label}</span>
                    </td>
                    <td>
                      <div className="row-actions">
                        <button title="Editar" onClick={() => setEditing(p)}>
                          <Edit3 />
                        </button>
                        <button title="Reabastecer" onClick={() => restock(p)}>
                          <RefreshCw />
                        </button>
                        <button
                          title="Eliminar"
                          className="delete"
                          onClick={() => remove(p)}
                        >
                          <Trash2 />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {!rows.length && (
          <div className="empty">
            <Package />
            <b>No hay medicamentos</b>
            <p>
              Ajusta los filtros o agrega el primer medicamento de esta
              sucursal.
            </p>
          </div>
        )}
      </section>
      {editing && (
        <MedicineModal
          medicine={editing}
          onClose={() => setEditing(null)}
          onSave={save}
        />
      )}
      {deleteDialog}
    </>
  );
}

function Dashboard({ items, branch, onInventory, user }) {
  const critical = items.filter((p) => p.stock <= p.min),
    value = items.reduce((s, p) => s + p.stock * p.buyPrice, 0);
  const [metrics, setMetrics] = useState(null);
  useEffect(() => {
    fetch(`/api/v1/dashboard/?branch=${encodeURIComponent(branch.id)}`, { credentials: "same-origin" })
      .then((response) => response.ok ? response.json() : null)
      .then((data) => data && setMetrics(data));
  }, [branch.id]);
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">{branch.name.toUpperCase()}</p>
          <h1>Buenos días, {user?.name || "Usuario"}</h1>
          <p>Este es el estado general de tu inventario hoy.</p>
        </div>
        <button className="button secondary" onClick={onInventory}>
          Ver inventario
        </button>
      </section>
      <div className="kpi-grid">
        {[
          [Package, "Medicamentos", items.length, "Registrados"],
          [
            BarChart3,
            "Valor del inventario",
            money(metrics?.inventoryValue ?? value),
            "A precio de compra",
          ],
          [
            AlertTriangle,
            "Stock crítico",
            metrics?.critical ?? critical.length,
            "Requieren atención",
          ],
          [ShoppingCart, "Ventas de hoy", money(metrics?.salesToday), "Registradas en Supabase"],
          [AlertTriangle, "Pérdida por vencimiento", money(metrics?.expiredLoss), "Lotes vencidos valorizados"],
        ].map(([Icon, label, value, note], i) => (
          <article className="kpi" key={label}>
            <span className={`kpi-icon c${i}`}>
              <Icon />
            </span>
            <div>
              <small>{label}</small>
              <b>{value}</b>
              <p>{note}</p>
            </div>
          </article>
        ))}
      </div>
      <div className="dashboard-grid">
        <section className="panel">
          <header>
            <div>
              <h3>Comparación entre farmacias</h3>
              <p>Ventas acumuladas del mes desde Supabase</p>
            </div>
          </header>
          <div className="chart">
            <ResponsiveContainer>
              <AreaChart data={metrics?.branches || []}>
                <defs>
                  <linearGradient id="area" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0" stopColor="#2563eb" stopOpacity=".25" />
                    <stop offset="1" stopColor="#2563eb" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="#e9edf4" />
                <XAxis dataKey="name" axisLine={false} tickLine={false} />
                <YAxis axisLine={false} tickLine={false} />
                <Tooltip />
                <Area
                  dataKey="sales"
                  stroke="#2563eb"
                  strokeWidth={3}
                  fill="url(#area)"
                  type="monotone"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>
        <section className="panel alerts-panel">
          <header>
            <div>
              <h3>Alertas de stock</h3>
              <p>Medicamentos que necesitan atención</p>
            </div>
          </header>
          {critical.slice(0, 5).map((p) => (
            <div className="alert-row" key={p.id}>
              <span>
                <AlertTriangle />
              </span>
              <div>
                <b>{p.name}</b>
                <small>
                  {p.stock === 0
                    ? "Agotado"
                    : `${p.stock} unidades disponibles`}
                </small>
              </div>
              <button onClick={onInventory}>Revisar</button>
            </div>
          ))}
          {!critical.length && (
            <div className="empty compact">
              <b>Todo en orden</b>
              <p>No hay alertas en esta sucursal.</p>
            </div>
          )}
        </section>
      </div>
    </>
  );
}

function SimpleModal({ title, onClose, children }) {
  return (
    <div
      className="modal-backdrop"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <section className="modal-card small-modal">
        <header>
          <h2>{title}</h2>
          <button className="icon-button" onClick={onClose}>
            <X />
          </button>
        </header>
        {children}
      </section>
    </div>
  );
}

function BranchManager({
  branches,
  setBranches,
  inventories,
  setInventories,
  branchId,
  setBranchId,
}) {
  const [form, setForm] = useState(null);
  const [askDelete, deleteDialog] = useDeleteConfirmation();
  const save = (e) => {
    e.preventDefault();
    if (form.id)
      setBranches(branches.map((b) => (b.id === form.id ? form : b)));
    else {
      const id = `sucursal-${Date.now()}`;
      setBranches([...branches, { ...form, id, active: true }]);
      setInventories({ ...inventories, [id]: [] });
    }
    setForm(null);
  };
  const remove = async (b) => {
    if (b.id === branchId)
      return alert("No puedes eliminar la sucursal activa.");
    if ((inventories[b.id] || []).length)
      return alert(
        "La sucursal tiene inventario. Trasládalo o elimínalo antes.",
      );
    const accepted = await askDelete({
      title: `¿Eliminar ${b.name}?`,
      message:
        "La sucursal y su configuración dejarán de estar disponibles. Esta acción no se puede deshacer.",
    });
    if (accepted) {
      try {
        await deleteRemote("branches", b.id);
        setBranches(branches.filter((x) => x.id !== b.id));
      } catch (error) {
        alert(error.message);
      }
    }
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">RED DE FARMACIAS</p>
          <h1>Sucursales</h1>
          <p>Crea, edita y administra todas tus sedes.</p>
        </div>
        <button
          className="button primary"
          onClick={() =>
            setForm({
              name: "",
              code: "",
              address: "",
              city: "",
              phone: "",
              manager: "",
              active: true,
            })
          }
        >
          <Plus />
          Nueva sucursal
        </button>
      </section>
      <div className="branch-grid">
        {branches.map((b) => {
          const items = inventories[b.id] || [];
          return (
            <article className="branch-card" key={b.id}>
              <span>
                <Building2 />
              </span>
              <h3>{b.name}</h3>
              <p>
                {b.address}
                {b.city && ` · ${b.city}`}
              </p>
              <p>
                {b.phone || "Sin teléfono"} · {b.manager || "Sin responsable"}
              </p>
              <div>
                <b>
                  {items.length}
                  <small>Medicamentos</small>
                </b>
                <b>
                  {items.reduce((s, p) => s + p.stock, 0)}
                  <small>Unidades</small>
                </b>
              </div>
              <span
                className={`status ${b.active !== false ? "success" : "danger"}`}
              >
                {b.id === branchId
                  ? "Seleccionada"
                  : b.active !== false
                    ? "Operativa"
                    : "Inactiva"}
              </span>
              <div className="card-actions">
                <button
                  className="button secondary"
                  disabled={b.id === branchId || b.active === false}
                  onClick={() => setBranchId(b.id)}
                >
                  Administrar
                </button>
                <button
                  className="icon-button"
                  onClick={() => setForm({ ...b })}
                >
                  <Edit3 />
                </button>
                <button
                  className="icon-button delete"
                  onClick={() => remove(b)}
                >
                  <Trash2 />
                </button>
              </div>
            </article>
          );
        })}
      </div>
      {form && (
        <SimpleModal
          title={form.id ? "Editar sucursal" : "Nueva sucursal"}
          onClose={() => setForm(null)}
        >
          <form className="simple-form" onSubmit={save}>
            <div className="form-grid">
              {[
                ["Nombre", "name"],
                ["Código", "code"],
                ["Dirección", "address"],
                ["Ciudad", "city"],
                ["Teléfono", "phone"],
                ["Responsable", "manager"],
              ].map(([label, key]) => (
                <label key={key}>
                  {label}
                  <input
                    value={form[key] || ""}
                    onChange={(e) =>
                      setForm({ ...form, [key]: e.target.value })
                    }
                    required={["name", "code"].includes(key)}
                  />
                </label>
              ))}
            </div>
            <label className="check-row">
              <input
                type="checkbox"
                checked={form.active !== false}
                onChange={(e) => setForm({ ...form, active: e.target.checked })}
              />{" "}
              Sucursal activa
            </label>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary">Guardar sucursal</button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {deleteDialog}
    </>
  );
}

function Purchases({ branch, items, suppliers }) {
  const [purchases, setPurchases] = useState([]),
    [form, setForm] = useState(null),
    [receiving, setReceiving] = useState(null),
    [supplierReturn, setSupplierReturn] = useState(null),
    [busy, setBusy] = useState(false);
  const [askConfirm, actionDialog] = useActionConfirmation();
  const load = async () => {
    const response = await fetch("/api/v1/purchases/", {
      credentials: "same-origin",
    });
    if (response.ok) setPurchases((await response.json()).purchases || []);
  };
  useEffect(() => {
    load();
  }, []);
  const create = async (event) => {
    event.preventDefault();
    const accepted = await askConfirm({
      icon: ClipboardList,
      eyebrow: "CONFIRMAR ORDEN",
      title: "¿Crear esta orden de compra?",
      message:
        "La orden quedará registrada y lista para recibir mercadería por lote.",
      confirmLabel: "Crear orden",
    });
    if (!accepted) return;
    setBusy(true);
    try {
      const response = await fetch("/api/v1/purchases/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify({
          branchId: branch.id,
          supplierId: form.supplierId,
          notes: form.notes,
          items: [
            {
              productId: form.productId,
              quantity: form.quantity,
              cost: form.cost,
            },
          ],
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      setPurchases([data, ...purchases]);
      setForm(null);
    } catch (error) {
      alert(error.message);
    } finally {
      setBusy(false);
    }
  };
  const receive = async (event) => {
    event.preventDefault(); setBusy(true);
    const response = await fetch(`/api/v1/purchases/${receiving.purchase.id}/receive/`, { method:"POST", credentials:"same-origin", headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken()}, body:JSON.stringify({items:[{detailId:receiving.detailId,quantity:receiving.quantity,lot:receiving.lot,expires:receiving.expires}]}) });
    const data=await response.json(); setBusy(false); if(!response.ok)return alert(data.detail);
    setPurchases(purchases.map(x=>x.id===data.id?data:x)); setReceiving(null);
  };
  const cancelPurchase = async (purchase) => {
    const reason=window.prompt("Motivo de anulación:"); if(!reason)return;
    if(!await askConfirm({icon:Trash2,tone:"danger",eyebrow:"ANULAR ORDEN",title:`¿Anular ${purchase.number}?`,message:"Se cancelará el saldo pendiente. Las recepciones ya realizadas conservarán su trazabilidad.",confirmLabel:"Anular orden"}))return;
    const response=await fetch(`/api/v1/purchases/${purchase.id}/cancel/`,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken()},body:JSON.stringify({reason})});const data=await response.json();if(!response.ok)return alert(data.detail);setPurchases(purchases.map(x=>x.id===data.id?data:x));
  };
  const returnSupplier = async(event)=>{event.preventDefault();if(!await askConfirm({icon:Truck,tone:"danger",eyebrow:"DEVOLUCIÓN A PROVEEDOR",title:"¿Confirmar salida del lote?",message:"Las unidades saldrán del inventario y quedarán registradas contra la compra original.",confirmLabel:"Devolver"}))return;setBusy(true);const response=await fetch(`/api/v1/purchases/${supplierReturn.purchase.id}/return/`,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken()},body:JSON.stringify({lotId:supplierReturn.lotId,quantity:supplierReturn.quantity,reason:supplierReturn.reason})});const data=await response.json();setBusy(false);if(!response.ok)return alert(data.detail);setSupplierReturn(null);};
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">ABASTECIMIENTO</p>
          <h1>Órdenes de compra</h1>
          <p>Recepción controlada por lote y vencimiento en {branch.name}.</p>
        </div>
        <button
          className="button primary"
          disabled={!items.length || !suppliers.length}
          onClick={() =>
            setForm({
              supplierId: suppliers[0]?.id,
              productId: items[0]?.id,
              quantity: 1,
              cost: items[0]?.buyPrice || 0,
              notes: "",
            })
          }
        >
          <Plus />
          Nueva orden
        </button>
      </section>
      <section className="table-card">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Orden</th>
                <th>Proveedor</th>
                <th>Fecha</th>
                <th>Total</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {purchases.map((purchase) => (
                <tr key={purchase.id}>
                  <td>
                    <b>{purchase.number}</b>
                    <small>{purchase.user}</small>
                  </td>
                  <td>{purchase.supplier}</td>
                  <td>{new Date(purchase.date).toLocaleDateString("es-EC")}</td>
                  <td>{money(purchase.total)}</td>
                  <td>
                    <span className="status success">{purchase.status}</span>
                  </td>
                  <td><div className="row-actions">{!["RECIBIDA","ANULADA"].includes(purchase.status)&&<button title="Recibir" onClick={()=>{const detail=purchase.items.find(x=>x.received<x.ordered);setReceiving({purchase,detailId:detail?.id,quantity:detail?detail.ordered-detail.received:1,lot:"",expires:""});}}><Package/></button>}{purchase.receipts?.length>0&&<button title="Devolver al proveedor" onClick={()=>setSupplierReturn({purchase,lotId:purchase.receipts[0].lotId,quantity:1,reason:""})}><Truck/></button>}{!["RECIBIDA","ANULADA"].includes(purchase.status)&&<button className="delete" title="Anular" onClick={()=>cancelPurchase(purchase)}><Trash2/></button>}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {form && (
        <SimpleModal
          title="Nueva orden de compra"
          onClose={() => setForm(null)}
        >
          <form className="simple-form" onSubmit={create}>
            <div className="form-grid">
              <label>
                Proveedor
                <select
                  value={form.supplierId}
                  onChange={(e) =>
                    setForm({ ...form, supplierId: e.target.value })
                  }
                >
                  {suppliers.map((x) => (
                    <option value={x.id} key={x.id}>
                      {x.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Medicamento
                <select
                  value={form.productId}
                  onChange={(e) =>
                    setForm({ ...form, productId: e.target.value })
                  }
                >
                  {items.map((x) => (
                    <option value={x.id} key={x.id}>
                      {x.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Cantidad
                <input
                  required
                  min="1"
                  type="number"
                  value={form.quantity}
                  onChange={(e) =>
                    setForm({ ...form, quantity: e.target.value })
                  }
                />
              </label>
              <label>
                Costo unitario
                <input
                  required
                  min="0"
                  step="0.01"
                  type="number"
                  value={form.cost}
                  onChange={(e) => setForm({ ...form, cost: e.target.value })}
                />
              </label>
              <label className="wide">
                Observación
                <input
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                />
              </label>
            </div>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary" disabled={busy}>
                {busy ? "Guardando…" : "Crear orden"}
              </button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {receiving && <SimpleModal title={`Recibir ${receiving.purchase.number}`} onClose={()=>setReceiving(null)}><form className="simple-form" onSubmit={receive}><div className="form-grid"><label>Producto<select value={receiving.detailId} onChange={e=>setReceiving({...receiving,detailId:e.target.value})}>{receiving.purchase.items.filter(x=>x.received<x.ordered).map(x=><option value={x.id} key={x.id}>{x.product} · pendiente {x.ordered-x.received}</option>)}</select></label><label>Cantidad<input type="number" min="1" required value={receiving.quantity} onChange={e=>setReceiving({...receiving,quantity:e.target.value})}/></label><label>Número de lote<input required value={receiving.lot} onChange={e=>setReceiving({...receiving,lot:e.target.value})}/></label><label>Vencimiento<input type="date" required value={receiving.expires} onChange={e=>setReceiving({...receiving,expires:e.target.value})}/></label></div><footer><button type="button" className="button secondary" onClick={()=>setReceiving(null)}>Cancelar</button><button className="button primary" disabled={busy}>{busy?"Recibiendo…":"Confirmar recepción"}</button></footer></form></SimpleModal>}
      {supplierReturn&&<SimpleModal title="Devolución al proveedor" onClose={()=>setSupplierReturn(null)}><form className="simple-form" onSubmit={returnSupplier}><div className="form-grid"><label>Lote<select value={supplierReturn.lotId} onChange={e=>setSupplierReturn({...supplierReturn,lotId:e.target.value})}>{supplierReturn.purchase.receipts.map(x=><option key={x.lotId} value={x.lotId}>{x.product} · {x.lot}</option>)}</select></label><label>Cantidad<input type="number" min="1" required value={supplierReturn.quantity} onChange={e=>setSupplierReturn({...supplierReturn,quantity:e.target.value})}/></label><label className="wide">Motivo<input required value={supplierReturn.reason} onChange={e=>setSupplierReturn({...supplierReturn,reason:e.target.value})}/></label></div><footer><button type="button" className="button secondary" onClick={()=>setSupplierReturn(null)}>Cancelar</button><button className="button primary" disabled={busy}>Continuar</button></footer></form></SimpleModal>}
      {actionDialog}
    </>
  );
}

function Suppliers({ suppliers, setSuppliers }) {
  const [form, setForm] = useState(null),
    [query, setQuery] = useState("");
  const [askDelete, deleteDialog] = useDeleteConfirmation();
  const rows = suppliers.filter((s) =>
    (s.name + s.taxId + s.contact).toLowerCase().includes(query.toLowerCase()),
  );
  const save = (e) => {
    e.preventDefault();
    if (form.id)
      setSuppliers(suppliers.map((s) => (s.id === form.id ? form : s)));
    else
      setSuppliers([...suppliers, { ...form, id: Date.now(), active: true }]);
    setForm(null);
  };
  const remove = async (supplier) => {
    const accepted = await askDelete({
      title: `¿Eliminar ${supplier.name}?`,
      message:
        "El proveedor se eliminará del directorio. Los medicamentos existentes conservarán sus datos actuales.",
    });
    if (accepted) {
      try {
        await deleteRemote("suppliers", supplier.id);
        setSuppliers(suppliers.filter((item) => item.id !== supplier.id));
      } catch (error) {
        alert(error.message);
      }
    }
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">ABASTECIMIENTO</p>
          <h1>Proveedores</h1>
          <p>Directorio de laboratorios y distribuidores.</p>
        </div>
        <button
          className="button primary"
          onClick={() =>
            setForm({
              name: "",
              taxId: "",
              contact: "",
              phone: "",
              email: "",
              city: "",
              active: true,
            })
          }
        >
          <Plus />
          Nuevo proveedor
        </button>
      </section>
      <section className="filter-card supplier-filter">
        <div className="search-box">
          <Search />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar proveedor, NIT o contacto"
          />
        </div>
      </section>
      <div className="supplier-grid">
        {rows.map((s) => (
          <article className="supplier-card" key={s.id}>
            <div>
              <span>
                <Truck />
              </span>
              <span className={`status ${s.active ? "success" : "danger"}`}>
                {s.active ? "Activo" : "Inactivo"}
              </span>
            </div>
            <h3>{s.name}</h3>
            <p>NIT {s.taxId}</p>
            <dl>
              <dt>Contacto</dt>
              <dd>{s.contact}</dd>
              <dt>Teléfono</dt>
              <dd>{s.phone}</dd>
              <dt>Correo</dt>
              <dd>{s.email}</dd>
              <dt>Ciudad</dt>
              <dd>{s.city}</dd>
            </dl>
            <footer>
              <button
                className="button secondary"
                onClick={() => setForm({ ...s })}
              >
                <Edit3 />
                Editar
              </button>
              <button className="icon-button delete" onClick={() => remove(s)}>
                <Trash2 />
              </button>
            </footer>
          </article>
        ))}
      </div>
      {form && (
        <SimpleModal
          title={form.id ? "Editar proveedor" : "Nuevo proveedor"}
          onClose={() => setForm(null)}
        >
          <form className="simple-form" onSubmit={save}>
            <div className="form-grid">
              {[
                ["Razón social", "name"],
                ["NIT / RUC", "taxId"],
                ["Contacto", "contact"],
                ["Teléfono", "phone"],
                ["Correo", "email"],
                ["Ciudad", "city"],
              ].map(([label, key]) => (
                <label key={key}>
                  {label}
                  <input
                    type={key === "email" ? "email" : "text"}
                    value={form[key]}
                    onChange={(e) =>
                      setForm({ ...form, [key]: e.target.value })
                    }
                    required={["name", "taxId"].includes(key)}
                  />
                </label>
              ))}
            </div>
            <label className="check-row">
              <input
                type="checkbox"
                checked={form.active}
                onChange={(e) => setForm({ ...form, active: e.target.checked })}
              />{" "}
              Proveedor activo
            </label>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary">Guardar proveedor</button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {deleteDialog}
    </>
  );
}

function Sales({ items, setItems, sales, setSales, branch }) {
  const [form, setForm] = useState(null),
    [adjustment, setAdjustment] = useState(null),
    [saving, setSaving] = useState(false);
  const [askConfirm, adjustmentDialog] = useActionConfirmation();
  const total = form
    ? Number(form.qty || 0) *
      (items.find((p) => p.id === Number(form.productId))?.sellPrice || 0)
    : 0;
  const save = async (e) => {
    e.preventDefault();
    const product = items.find((p) => p.id === Number(form.productId)),
      qty = Number(form.qty);
    if (!product || qty < 1) return;
    if (qty > product.stock)
      return alert("No hay stock suficiente para completar la venta.");
    setSaving(true);
    try {
      const response = await fetch("/api/v1/sales/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify({
          branchId: branch.id,
          productId: product.id,
          qty,
          customer: form.customer,
          payment: form.payment,
        }),
      });
      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail || "No se pudo registrar la venta.");
      setItems(
        items.map((p) =>
          p.id === product.id ? { ...p, stock: data.stock } : p,
        ),
      );
      setSales([
        data.sale,
        ...sales.filter((sale) => sale.id !== data.sale.id),
      ]);
      setForm(null);
    } catch (error) {
      alert(error.message);
    } finally {
      setSaving(false);
    }
  };
  const submitAdjustment = async (event) => {
    event.preventDefault();
    const isReturn=adjustment.kind==="return";
    if(!await askConfirm({icon:isReturn?RefreshCw:Trash2,tone:isReturn?"primary":"danger",eyebrow:isReturn?"DEVOLUCIÓN Y NOTA DE CRÉDITO":"ANULAR VENTA",title:isReturn?"¿Confirmar devolución?":"¿Anular esta venta?",message:isReturn?"Se repondrá el lote original y se generará una nota de crédito.":"Se revertirá todo el inventario consumido y el movimiento de caja.",confirmLabel:isReturn?"Devolver":"Anular venta"}))return;
    setSaving(true);const response=await fetch(`/api/v1/sales/${adjustment.sale.id}/${isReturn?"return":"cancel"}/`,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-CSRFToken":csrfToken()},body:JSON.stringify({quantity:adjustment.quantity,reason:adjustment.reason})});const data=await response.json();setSaving(false);if(!response.ok)return alert(data.detail);setItems(items.map(x=>x.id===Number(adjustment.sale.productId||items.find(p=>p.sku===adjustment.sale.sku)?.id)?{...x,stock:data.stock}:x));if(!isReturn)setSales(sales.map(x=>x.id===adjustment.sale.id?{...x,cancelled:true}:x));setAdjustment(null);
  };
  const rows = sales.filter((s) => s.branchId === branch.id);
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">PUNTO DE VENTA</p>
          <h1>Ventas</h1>
          <p>Historial de {branch.name}.</p>
        </div>
        <button
          className="button primary"
          disabled={!items.length}
          onClick={() =>
            setForm({ productId: items[0]?.id, qty: 1, customer: "", payment: "EFECTIVO" })
          }
        >
          <Plus />
          Registrar venta
        </button>
      </section>
      <div className="kpi-grid sales-kpis">
        <article className="kpi">
          <span className="kpi-icon c1">
            <ShoppingCart />
          </span>
          <div>
            <small>Ventas registradas</small>
            <b>{rows.length}</b>
            <p>Sucursal actual</p>
          </div>
        </article>
        <article className="kpi">
          <span className="kpi-icon">
            <BarChart3 />
          </span>
          <div>
            <small>Total vendido</small>
            <b>{money(rows.reduce((s, x) => s + x.total, 0))}</b>
            <p>Histórico local</p>
          </div>
        </article>
      </div>
      <section className="table-card sales-table">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Medicamento</th>
                <th>Cliente</th>
                <th>Cantidad</th>
                <th>Total</th>
                <th>Pago</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr key={s.id}>
                  <td>{s.date}</td>
                  <td>
                    <b>{s.product}</b>
                    <small>{s.sku}</small>
                  </td>
                  <td>{s.customer}</td>
                  <td>{s.qty}</td>
                  <td>
                    <b>{money(s.total)}</b>
                  </td>
                  <td>{s.payment || "No registrado"}</td>
                  <td><div className="row-actions">{!s.cancelled&&<button title="Devolver" onClick={()=>setAdjustment({kind:"return",sale:s,quantity:1,reason:""})}><RefreshCw/></button>}{!s.cancelled&&<button className="delete" title="Anular" onClick={()=>setAdjustment({kind:"cancel",sale:s,reason:""})}><Trash2/></button>}</div></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!rows.length && (
          <div className="empty">
            <ShoppingCart />
            <b>Sin ventas registradas</b>
            <p>Registra la primera venta de esta sucursal.</p>
          </div>
        )}
      </section>
      {form && (
        <SimpleModal title="Registrar venta" onClose={() => setForm(null)}>
          <form className="simple-form" onSubmit={save}>
            <div className="form-grid">
              <label className="wide">
                Medicamento
                <select
                  value={form.productId}
                  onChange={(e) =>
                    setForm({ ...form, productId: e.target.value })
                  }
                >
                  {items
                    .filter((p) => p.stock > 0)
                    .map((p) => (
                      <option value={p.id} key={p.id}>
                        {p.name} · {p.stock} disponibles
                      </option>
                    ))}
                </select>
              </label>
              <label>
                Cantidad
                <input
                  type="number"
                  min="1"
                  value={form.qty}
                  onChange={(e) => setForm({ ...form, qty: e.target.value })}
                />
              </label>
              <label>
                Cliente
                <input
                  value={form.customer}
                  onChange={(e) =>
                    setForm({ ...form, customer: e.target.value })
                  }
                  placeholder="Consumidor final"
                />
              </label>
              <label>
                Forma de pago
                <select value={form.payment} onChange={(e) => setForm({ ...form, payment: e.target.value })}>
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="TARJETA">Tarjeta</option>
                  <option value="TRANSFERENCIA">Transferencia</option>
                </select>
              </label>
            </div>
            <div className="sale-total">
              <span>Total de la venta</span>
              <b>{money(total)}</b>
            </div>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary" disabled={saving}>
                {saving ? "Registrando…" : "Confirmar venta"}
              </button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {adjustment&&<SimpleModal title={adjustment.kind==="return"?"Devolución de cliente":"Anular venta"} onClose={()=>setAdjustment(null)}><form className="simple-form" onSubmit={submitAdjustment}><div className="form-grid">{adjustment.kind==="return"&&<label>Cantidad<input type="number" min="1" max={adjustment.sale.qty} required value={adjustment.quantity} onChange={e=>setAdjustment({...adjustment,quantity:e.target.value})}/></label>}<label className="wide">Motivo<input required value={adjustment.reason} onChange={e=>setAdjustment({...adjustment,reason:e.target.value})}/></label></div><footer><button type="button" className="button secondary" onClick={()=>setAdjustment(null)}>Cancelar</button><button className="button primary" disabled={saving}>Continuar</button></footer></form></SimpleModal>}
      {adjustmentDialog}
    </>
  );
}

function Alerts({ items, setItems, branch, lotAlerts }) {
  const alerts = items.filter((p) => p.stock <= p.min);
  const expiring = lotAlerts.filter((lot) => lot.branchId === branch.id);
  const restock = (p) => {
    const qty = Number(
      prompt(
        `Cantidad a ingresar para ${p.name}:`,
        Math.max(p.min * 2 - p.stock, 1),
      ),
    );
    if (qty > 0)
      setItems(
        items.map((x) => (x.id === p.id ? { ...x, stock: x.stock + qty } : x)),
      );
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">REABASTECIMIENTO</p>
          <h1>Alertas</h1>
          <p>
            {alerts.length + expiring.length} alertas activas en {branch.name}.
          </p>
        </div>
      </section>
      <section className="table-card">
        <div className="table-title">
          <div>
            <h3>Lotes y vencimientos</h3>
            <p>Ordenados por fecha para aplicar FEFO.</p>
          </div>
        </div>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Medicamento</th>
                <th>Lote</th>
                <th>Vencimiento</th>
                <th>Unidades</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {expiring.map((lot) => (
                <tr key={lot.id}>
                  <td>
                    <b>{lot.product}</b>
                    <small>{lot.sku}</small>
                  </td>
                  <td>{lot.number}</td>
                  <td>{lot.expires}</td>
                  <td>{lot.quantity}</td>
                  <td>
                    <span
                      className={`status ${lot.status === "EXPIRED" ? "danger" : "warning"}`}
                    >
                      {lot.status === "EXPIRED"
                        ? "Vencido y bloqueado"
                        : "Próximo a vencer"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      <section className="alert-list">
        {alerts.map((p) => {
          const [label, tone] = getStatus(p);
          return (
            <article key={p.id}>
              <span className={tone}>
                <AlertTriangle />
              </span>
              <div>
                <b>{p.name}</b>
                <p>
                  {p.sku} · {p.presentation} · {p.lab}
                </p>
              </div>
              <div className="alert-stock">
                <b>{p.stock}</b>
                <small>Mínimo {p.min}</small>
              </div>
              <span className={`status ${tone}`}>{label}</span>
              <button className="button primary" onClick={() => restock(p)}>
                <RefreshCw />
                Reabastecer
              </button>
            </article>
          );
        })}
        {!alerts.length && (
          <div className="empty page-empty">
            <Bell />
            <b>Inventario saludable</b>
            <p>No existen medicamentos agotados o en nivel crítico.</p>
          </div>
        )}
      </section>
    </>
  );
}

function CashRegister({ branch }) {
  const [session, setSession] = useState(null),
    [form, setForm] = useState(null),
    [busy, setBusy] = useState(false);
  const load = async () => {
    const response = await fetch(
      `/api/v1/cash/session/?branch=${encodeURIComponent(branch.id)}`,
      { credentials: "same-origin" },
    );
    if (response.ok) setSession((await response.json()).session);
  };
  useEffect(() => {
    load();
  }, [branch.id]);
  const send = async (url, payload) => {
    setBusy(true);
    try {
      const response = await fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      setSession(data.closed ? null : data);
      setForm(null);
    } catch (error) {
      alert(error.message);
    } finally {
      setBusy(false);
    }
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">CONTROL DE EFECTIVO</p>
          <h1>Caja diaria</h1>
          <p>
            {session
              ? `Caja abierta · saldo esperado ${money(session.expected)}`
              : `No hay una caja abierta en ${branch.name}.`}
          </p>
        </div>
        {!session && (
          <button
            className="button primary"
            onClick={() => setForm({ kind: "open", initial: 0 })}
          >
            <Plus />
            Abrir caja
          </button>
        )}
      </section>
      {session && (
        <>
          <div className="kpi-grid sales-kpis">
            <article className="kpi">
              <span className="kpi-icon">
                <Wallet />
              </span>
              <div>
                <small>Saldo inicial</small>
                <b>{money(session.initial)}</b>
              </div>
            </article>
            <article className="kpi">
              <span className="kpi-icon">
                <BarChart3 />
              </span>
              <div>
                <small>Saldo esperado</small>
                <b>{money(session.expected)}</b>
              </div>
            </article>
          </div>
          <section className="page-heading">
            <button
              className="button secondary"
              onClick={() =>
                setForm({
                  kind: "movement",
                  type: "INGRESO",
                  amount: "",
                  notes: "",
                })
              }
            >
              Registrar movimiento
            </button>
            <button
              className="button primary"
              onClick={() =>
                setForm({ kind: "close", declared: session.expected })
              }
            >
              Cerrar caja
            </button>
          </section>
          <section className="table-card">
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Tipo</th>
                    <th>Forma de pago</th>
                    <th>Detalle</th>
                    <th>Monto</th>
                  </tr>
                </thead>
                <tbody>
                  {session.movements.map((x) => (
                    <tr key={x.id}>
                      <td>{new Date(x.date).toLocaleString("es-EC")}</td>
                      <td>{x.type}</td>
                      <td>{x.payment}</td>
                      <td>{x.notes}</td>
                      <td>
                        <b>{money(x.amount)}</b>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
      {form && (
        <SimpleModal
          title={
            form.kind === "open"
              ? "Abrir caja"
              : form.kind === "close"
                ? "Cerrar caja"
                : "Movimiento de caja"
          }
          onClose={() => setForm(null)}
        >
          <form
            className="simple-form"
            onSubmit={(e) => {
              e.preventDefault();
              if (form.kind === "open")
                send("/api/v1/cash/session/", {
                  branchId: branch.id,
                  initial: form.initial,
                });
              else if (form.kind === "close")
                send(`/api/v1/cash/session/${session.id}/close/`, {
                  declared: form.declared,
                });
              else send(`/api/v1/cash/session/${session.id}/movement/`, form);
            }}
          >
            <div className="form-grid">
              {form.kind === "movement" && (
                <>
                  <label>
                    Tipo
                    <select
                      value={form.type}
                      onChange={(e) =>
                        setForm({ ...form, type: e.target.value })
                      }
                    >
                      <option value="INGRESO">Ingreso</option>
                      <option value="GASTO">Gasto</option>
                      <option value="RETIRO">Retiro</option>
                    </select>
                  </label>
                  <label>
                    Detalle
                    <input
                      value={form.notes}
                      onChange={(e) =>
                        setForm({ ...form, notes: e.target.value })
                      }
                    />
                  </label>
                </>
              )}
              <label className="wide">
                {form.kind === "close" ? "Efectivo contado" : "Monto"}
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  required
                  value={form.initial ?? form.declared ?? form.amount}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      [form.kind === "open"
                        ? "initial"
                        : form.kind === "close"
                          ? "declared"
                          : "amount"]: e.target.value,
                    })
                  }
                />
              </label>
            </div>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary" disabled={busy}>
                {busy ? "Procesando…" : "Confirmar"}
              </button>
            </footer>
          </form>
        </SimpleModal>
      )}
    </>
  );
}

function Transfers({ branch, branches }) {
  const [rows, setRows] = useState([]),
    [lots, setLots] = useState([]),
    [form, setForm] = useState(null),
    [busy, setBusy] = useState(false);
  const [askConfirm, actionDialog] = useActionConfirmation();
  const load = async () => {
    const [a, b] = await Promise.all([
      fetch("/api/v1/transfers/", { credentials: "same-origin" }),
      fetch(`/api/v1/transfers/lots/?branch=${encodeURIComponent(branch.id)}`, {
        credentials: "same-origin",
      }),
    ]);
    if (a.ok) setRows((await a.json()).transfers || []);
    if (b.ok) setLots((await b.json()).lots || []);
  };
  useEffect(() => {
    load();
  }, [branch.id]);
  const create = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const response = await fetch("/api/v1/transfers/", {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify({
          origin: branch.id,
          destination: form.destination,
          items: [{ lotId: form.lotId, quantity: form.quantity }],
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail);
      setRows([data, ...rows]);
      setForm(null);
    } catch (error) {
      alert(error.message);
    } finally {
      setBusy(false);
    }
  };
  const action = async (row, name) => {
    const labels = {
      approve: [
        "Aprobar transferencia",
        "La solicitud quedará autorizada para despacho.",
        "Aprobar",
      ],
      dispatch: [
        "Despachar transferencia",
        "Las existencias saldrán del origen y quedarán en tránsito.",
        "Despachar",
      ],
      receive: [
        "Confirmar recepción",
        "Los lotes ingresarán al inventario de destino.",
        "Recibir",
      ],
    };
    const detail = labels[name];
    if (
      !(await askConfirm({
        icon: name === "dispatch" ? Truck : Package,
        eyebrow: "TRANSFERENCIA POR LOTES",
        title: detail[0],
        message: detail[1],
        confirmLabel: detail[2],
      }))
    )
      return;
    const response = await fetch(`/api/v1/transfers/${row.id}/${name}/`, {
      method: "POST",
      credentials: "same-origin",
      headers: { "X-CSRFToken": csrfToken() },
    });
    const data = await response.json();
    if (!response.ok) return alert(data.detail);
    setRows(rows.map((x) => (x.id === data.id ? data : x)));
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">TRAZABILIDAD ENTRE SEDES</p>
          <h1>Transferencias</h1>
          <p>Despacho y recepción controlados por lote.</p>
        </div>
        <button
          className="button primary"
          disabled={!lots.length || branches.length < 2}
          onClick={() =>
            setForm({
              destination: branches.find((x) => x.id !== branch.id)?.id,
              lotId: lots[0]?.id,
              quantity: 1,
            })
          }
        >
          <Plus />
          Nueva transferencia
        </button>
      </section>
      <section className="table-card">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Número</th>
                <th>Origen → destino</th>
                <th>Productos</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((x) => (
                <tr key={x.id}>
                  <td>
                    <b>{x.number}</b>
                    <small>{x.user}</small>
                  </td>
                  <td>
                    {x.origin} → {x.destination}
                  </td>
                  <td>
                    {x.items
                      .map((i) => `${i.product} · ${i.lot} (${i.quantity})`)
                      .join(", ")}
                  </td>
                  <td>
                    <span className="status success">{x.status}</span>
                  </td>
                  <td>
                    <div className="row-actions">
                      {x.status === "SOLICITADA" && (
                        <button
                          title="Aprobar"
                          onClick={() => action(x, "approve")}
                        >
                          <CheckCircle2 />
                        </button>
                      )}
                      {x.status === "APROBADA" && (
                        <button
                          title="Despachar"
                          onClick={() => action(x, "dispatch")}
                        >
                          <Truck />
                        </button>
                      )}
                      {x.status === "TRANSITO" && (
                        <button
                          title="Recibir"
                          onClick={() => action(x, "receive")}
                        >
                          <Package />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {form && (
        <SimpleModal title="Nueva transferencia" onClose={() => setForm(null)}>
          <form className="simple-form" onSubmit={create}>
            <div className="form-grid">
              <label>
                Destino
                <select
                  value={form.destination}
                  onChange={(e) =>
                    setForm({ ...form, destination: e.target.value })
                  }
                >
                  {branches
                    .filter((x) => x.id !== branch.id && x.active !== false)
                    .map((x) => (
                      <option key={x.id} value={x.id}>
                        {x.name}
                      </option>
                    ))}
                </select>
              </label>
              <label>
                Lote disponible
                <select
                  value={form.lotId}
                  onChange={(e) => setForm({ ...form, lotId: e.target.value })}
                >
                  {lots.map((x) => (
                    <option key={x.id} value={x.id}>
                      {x.product} · {x.number} · {x.quantity} u.
                    </option>
                  ))}
                </select>
              </label>
              <label className="wide">
                Cantidad
                <input
                  type="number"
                  min="1"
                  required
                  value={form.quantity}
                  onChange={(e) =>
                    setForm({ ...form, quantity: e.target.value })
                  }
                />
              </label>
            </div>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary" disabled={busy}>
                {busy ? "Procesando…" : "Solicitar"}
              </button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {actionDialog}
    </>
  );
}

function UserManagement({ users, setUsers, branches }) {
  const [form, setForm] = useState(null),
    [showPassword, setShowPassword] = useState(false);
  const [askDelete, deleteDialog] = useDeleteConfirmation();
  const save = (e) => {
    e.preventDefault();
    if (form.role !== "ADMIN" && !form.branchIds?.length)
      return alert("Selecciona al menos una farmacia para este usuario.");
    const payload = {
      ...form,
      branchIds:
        form.role === "ADMIN" ? branches.map((b) => b.id) : form.branchIds,
      active: form.active !== false,
    };
    if (form.id) setUsers(users.map((u) => (u.id === form.id ? payload : u)));
    else setUsers([...users, { ...payload, id: Date.now() }]);
    setForm(null);
  };
  const edit = (u) => setForm({ ...u, branchIds: u.branchIds || [] });
  const remove = async (user) => {
    const accepted = await askDelete({
      title: `¿Eliminar el acceso de ${user.name}?`,
      message:
        "El usuario perderá el acceso asignado al sistema. Esta acción no se puede deshacer.",
    });
    if (accepted) {
      try {
        await deleteRemote("users", user.id);
        setUsers(users.filter((item) => item.id !== user.id));
      } catch (error) {
        alert(error.message);
      }
    }
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">SEGURIDAD Y PERMISOS</p>
          <h1>Usuarios y accesos</h1>
          <p>Crea credenciales y asigna responsables a cada farmacia.</p>
        </div>
        <button
          className="button primary"
          onClick={() =>
            setForm({
              name: "",
              email: "",
              password: "",
              role: "INVENTARIO",
              branchIds: branches[0]?.id ? [branches[0].id] : [],
              active: true,
            })
          }
        >
          <Plus />
          Nuevo usuario
        </button>
      </section>
      <section className="table-card user-table">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Sucursales autorizadas</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className="medicine">
                      <span>
                        <Users />
                      </span>
                      <div>
                        <b>{u.name}</b>
                        <small>{u.email}</small>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="lab-badge">
                      {u.role === "ADMIN"
                        ? "Administrador"
                        : "Encargado de inventario"}
                    </span>
                  </td>
                  <td>
                    {u.role === "ADMIN"
                      ? "Todas las sucursales"
                      : u.branchIds
                          .map((id) => branches.find((b) => b.id === id)?.name)
                          .filter(Boolean)
                          .join(", ")}
                  </td>
                  <td>
                    <span
                      className={`status ${u.active ? "success" : "danger"}`}
                    >
                      {u.active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button title="Editar" onClick={() => edit(u)}>
                        <Edit3 />
                      </button>
                      <button
                        title="Eliminar"
                        className="delete"
                        onClick={() => remove(u)}
                      >
                        <Trash2 />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      {form && (
        <SimpleModal
          title={form.id ? "Editar credenciales" : "Crear credenciales"}
          onClose={() => setForm(null)}
        >
          <form className="simple-form" onSubmit={save}>
            <div className="form-grid">
              <label>
                Nombre completo
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              </label>
              <label>
                Correo de acceso
                <input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </label>
              <label>
                Contraseña temporal
                <div className="password-field">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={form.password}
                    onChange={(e) =>
                      setForm({ ...form, password: e.target.value })
                    }
                    minLength="8"
                    required={!form.id}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff /> : <Eye />}
                  </button>
                </div>
              </label>
              <label>
                Rol
                <select
                  value={form.role}
                  onChange={(e) => setForm({ ...form, role: e.target.value })}
                >
                  <option value="INVENTARIO">Encargado de inventario</option>
                  <option value="ADMIN">Administrador</option>
                </select>
              </label>
              {form.role !== "ADMIN" && (
                <fieldset className="wide branch-assignment">
                  <legend>Farmacias asignadas</legend>
                  {branches
                    .filter((b) => b.active !== false)
                    .map((b) => (
                      <label className="check-row" key={b.id}>
                        <input
                          type="checkbox"
                          checked={form.branchIds?.includes(b.id) || false}
                          onChange={(e) =>
                            setForm({
                              ...form,
                              branchIds: e.target.checked
                                ? [...(form.branchIds || []), b.id]
                                : (form.branchIds || []).filter(
                                    (id) => id !== b.id,
                                  ),
                            })
                          }
                        />
                        {b.name}
                      </label>
                    ))}
                </fieldset>
              )}
            </div>
            <label className="check-row">
              <input
                type="checkbox"
                checked={form.active !== false}
                onChange={(e) => setForm({ ...form, active: e.target.checked })}
              />{" "}
              Usuario activo
            </label>
            <div className="credential-note">
              El encargado utilizará este correo y contraseña para ingresar.
              Solo tendrá acceso operativo a la sucursal asignada.
            </div>
            <footer>
              <button
                type="button"
                className="button secondary"
                onClick={() => setForm(null)}
              >
                Cancelar
              </button>
              <button className="button primary">Guardar credenciales</button>
            </footer>
          </form>
        </SimpleModal>
      )}
      {deleteDialog}
    </>
  );
}

function Reports({ items, sales, branch }) {
  const rows = sales.filter((s) => s.branchId === branch.id);
  const download = (name, data) => {
    const csv = data
        .map((r) =>
          r.map((v) => `"${String(v).replaceAll('"', '""')}"`).join(","),
        )
        .join("\n"),
      a = document.createElement("a");
    a.href = URL.createObjectURL(
      new Blob(["\ufeff" + csv], { type: "text/csv" }),
    );
    a.download = name;
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <>
      <section className="page-heading">
        <div>
          <p className="eyebrow">ANÁLISIS OPERATIVO</p>
          <h1>Reportes</h1>
          <p>Indicadores y exportaciones de {branch.name}.</p>
        </div>
      </section>
      <div className="kpi-grid">
        {[
          ["Productos", items.length],
          ["Unidades", items.reduce((s, p) => s + p.stock, 0)],
          ["Stock crítico", items.filter((p) => p.stock <= p.min).length],
          ["Ventas", money(rows.reduce((s, v) => s + v.total, 0))],
        ].map(([label, value]) => (
          <article className="kpi" key={label}>
            <span className="kpi-icon">
              <BarChart3 />
            </span>
            <div>
              <small>{label}</small>
              <b>{value}</b>
              <p>Sucursal seleccionada</p>
            </div>
          </article>
        ))}
      </div>
      <div className="report-grid">
        <article className="panel">
          <Package />
          <h3>Inventario completo</h3>
          <p>Existencias, categorías, precios y laboratorios.</p>
          <button
            className="button secondary"
            onClick={() =>
              download("inventario.csv", [
                [
                  "SKU",
                  "Medicamento",
                  "Categoría",
                  "Laboratorio",
                  "Stock",
                  "Mínimo",
                  "Precio venta",
                ],
                ...items.map((p) => [
                  p.sku,
                  p.name,
                  p.category,
                  p.lab,
                  p.stock,
                  p.min,
                  p.sellPrice,
                ]),
              ])
            }
          >
            Descargar CSV
          </button>
        </article>
        <article className="panel">
          <AlertTriangle />
          <h3>Stock crítico</h3>
          <p>Medicamentos agotados o bajo el mínimo.</p>
          <button
            className="button secondary"
            onClick={() =>
              download("stock-critico.csv", [
                ["SKU", "Medicamento", "Stock", "Mínimo"],
                ...items
                  .filter((p) => p.stock <= p.min)
                  .map((p) => [p.sku, p.name, p.stock, p.min]),
              ])
            }
          >
            Descargar CSV
          </button>
        </article>
        <article className="panel">
          <ShoppingCart />
          <h3>Historial de ventas</h3>
          <p>Ventas realizadas en la sucursal seleccionada.</p>
          <button
            className="button secondary"
            onClick={() =>
              download("ventas.csv", [
                ["Fecha", "Medicamento", "Cliente", "Cantidad", "Total"],
                ...rows.map((v) => [
                  v.date,
                  v.product,
                  v.customer,
                  v.qty,
                  v.total,
                ]),
              ])
            }
          >
            Descargar CSV
          </button>
        </article>
      </div>
    </>
  );
}

function AdminReports({ branches, inventories, sales, users, onNotify }) {
  const [selected, setSelected] = useState("ALL"),
    [confirmExport, setConfirmExport] = useState(false),
    [exporting, setExporting] = useState(false),
    [dateFrom, setDateFrom] = useState(""),
    [dateTo, setDateTo] = useState(""),
    [selectedUser, setSelectedUser] = useState(""),
    [movement, setMovement] = useState(""),
    branch = branches.find((b) => b.id === selected),
    items =
      selected === "ALL"
        ? Object.values(inventories).flat()
        : inventories[selected] || [],
    rows =
      selected === "ALL" ? sales : sales.filter((s) => s.branchId === selected),
    label = selected === "ALL" ? "Todas las farmacias" : branch?.name;
  const downloadReport = async () => {
    setExporting(true);
    try {
      const params = new URLSearchParams({ branch: selected });
      if (dateFrom) params.set("from", dateFrom);
      if (dateTo) params.set("to", dateTo);
      if (selectedUser) params.set("user", selectedUser);
      if (movement) params.set("movement", movement);
      const response = await fetch(`/api/v1/reports/excel/?${params}`, {
        credentials: "same-origin",
      });
      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || "No se pudo generar el reporte.");
      }
      const url = URL.createObjectURL(await response.blob());
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `reporte-supabase-${new Date().toISOString().slice(0, 10)}.xlsx`;
      anchor.click();
      URL.revokeObjectURL(url);
      setConfirmExport(false);
      onNotify("El reporte se generó directamente desde Supabase.");
    } catch (error) {
      onNotify(error.message);
    } finally {
      setExporting(false);
    }
  };
  return (
    <>
      <section className="page-heading report-heading">
        <div>
          <p className="eyebrow">VISIÓN ADMINISTRATIVA</p>
          <h1>Reportes por farmacia</h1>
          <p>Compara el desempeño consolidado o revisa una sucursal.</p>
        </div>
        <select
          className="branch-select"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          <option value="ALL">Todas las farmacias</option>
          {branches.map((b) => (
            <option value={b.id} key={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <input
          className="branch-select"
          type="date"
          value={dateFrom}
          onChange={(e) => setDateFrom(e.target.value)}
          title="Fecha inicial"
        />
        <input
          className="branch-select"
          type="date"
          value={dateTo}
          onChange={(e) => setDateTo(e.target.value)}
          title="Fecha final"
        />
        <select
          className="branch-select"
          value={selectedUser}
          onChange={(e) => setSelectedUser(e.target.value)}
        >
          <option value="">Todos los usuarios</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.name}
            </option>
          ))}
        </select>
        <select
          className="branch-select"
          value={movement}
          onChange={(e) => setMovement(e.target.value)}
        >
          <option value="">Todos los movimientos</option>
          <option value="ENTRADA">Entradas</option>
          <option value="SALIDA">Salidas</option>
        </select>
        <button
          className="button primary report-download"
          onClick={() => setConfirmExport(true)}
        >
          <Download />
          Descargar Excel
        </button>
      </section>
      <div className="kpi-grid">
        {[
          ["Medicamentos", items.length],
          ["Unidades disponibles", items.reduce((s, p) => s + p.stock, 0)],
          ["Alertas críticas", items.filter((p) => p.stock <= p.min).length],
          ["Ventas acumuladas", money(rows.reduce((s, v) => s + v.total, 0))],
        ].map(([name, value]) => (
          <article className="kpi" key={name}>
            <span className="kpi-icon">
              <BarChart3 />
            </span>
            <div>
              <small>{name}</small>
              <b>{value}</b>
              <p>{label}</p>
            </div>
          </article>
        ))}
      </div>
      <section className="table-card branch-report">
        <table>
          <thead>
            <tr>
              <th>Farmacia</th>
              <th>Medicamentos</th>
              <th>Unidades</th>
              <th>Stock crítico</th>
              <th>Ventas</th>
            </tr>
          </thead>
          <tbody>
            {branches
              .filter((b) => selected === "ALL" || b.id === selected)
              .map((b) => {
                const inv = inventories[b.id] || [],
                  branchSales = sales.filter((s) => s.branchId === b.id);
                return (
                  <tr key={b.id}>
                    <td>
                      <b>{b.name}</b>
                      <small>{b.address}</small>
                    </td>
                    <td>{inv.length}</td>
                    <td>{inv.reduce((s, p) => s + p.stock, 0)}</td>
                    <td>
                      <span
                        className={`status ${inv.some((p) => p.stock <= p.min) ? "warning" : "success"}`}
                      >
                        {inv.filter((p) => p.stock <= p.min).length}
                      </span>
                    </td>
                    <td>
                      <b>
                        {money(branchSales.reduce((s, v) => s + v.total, 0))}
                      </b>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </section>
      {confirmExport && (
        <ConfirmDialog
          icon={FileSpreadsheet}
          eyebrow="EXPORTAR REPORTE"
          title="¿Descargar reporte en Excel?"
          message={`Se generará un archivo .xlsx con el resumen de ${label.toLowerCase()} y los datos visibles actualmente.`}
          confirmLabel="Sí, descargar"
          busy={exporting}
          onClose={() => setConfirmExport(false)}
          onConfirm={downloadReport}
        />
      )}
    </>
  );
}

export default function AppV2() {
  const [currentUser, setCurrentUser] = useState(null),
    [authChecking, setAuthChecking] = useState(true),
    [users, setUsers] = useState(
      () =>
        JSON.parse(localStorage.getItem("pharma-users") || "null") ||
        defaultUsers,
    ),
    [branches, setBranches] = useState(
      () =>
        JSON.parse(localStorage.getItem("pharma-branches") || "null") ||
        defaultBranches,
    ),
    [branchId, setBranchId] = useState(
      () => localStorage.getItem("pharma-branch") || "central",
    ),
    [inventories, setInventories] = useState(loadInventories),
    [suppliers, setSuppliers] = useState(
      () =>
        JSON.parse(localStorage.getItem("pharma-suppliers") || "null") ||
        defaultSuppliers,
    ),
    [sales, setSales] = useState(
      () => JSON.parse(localStorage.getItem("pharma-sales") || "null") || [],
    ),
    [lotAlerts, setLotAlerts] = useState([]),
    [active, setActive] = useState("Dashboard"),
    [sidebar, setSidebar] = useState(false),
    [modal, setModal] = useState(false),
    [logoutDialog, setLogoutDialog] = useState(false),
    [toast, setToast] = useState(""),
    [stateReady, setStateReady] = useState(false);
  useEffect(() => {
    const applyState = (state) => {
      setBranches(state.branches || []);
      setInventories(state.inventories || {});
      setSuppliers(state.suppliers || []);
      setSales(state.sales || []);
      if (state.users?.length) setUsers(state.users);
      const validBranch = state.branches?.some(
        (branch) => branch.id === branchId,
      )
        ? branchId
        : state.branches?.[0]?.id;
      if (validBranch) setBranchId(validBranch);
    };
    const load = async () => {
      try {
        const sessionResponse = await fetch("/api/v1/auth/session/", {
          credentials: "same-origin",
        });
        if (!sessionResponse.ok)
          throw new Error("No se pudo verificar la sesión.");
        const session = await sessionResponse.json();
        if (!session.authenticated) return;
        setCurrentUser(session.user);
        const stateResponse = await fetch("/api/v1/state/", {
          credentials: "same-origin",
        });
        if (!stateResponse.ok)
          throw new Error("No se pudieron cargar los datos desde Supabase.");
        let state = await stateResponse.json();
        if (state.empty && session.user.role === "ADMIN") {
          const migrationPayload = {
            branches,
            inventories,
            suppliers,
            sales,
            users: state.users || [],
          };
          const migrationResponse = await fetch("/api/v1/state/", {
            method: "PUT",
            credentials: "same-origin",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken(),
            },
            body: JSON.stringify(migrationPayload),
          });
          if (!migrationResponse.ok)
            throw new Error("No se pudo migrar la información local.");
          state = await migrationResponse.json();
        }
        applyState(state);
        const alertResponse = await fetch("/api/v1/lots/alerts/?days=90", {
          credentials: "same-origin",
        });
        if (alertResponse.ok)
          setLotAlerts((await alertResponse.json()).lots || []);
        [
          "pharma-inventories",
          "pharma-branches",
          "pharma-suppliers",
          "pharma-sales",
          "pharma-users",
        ].forEach((key) => localStorage.removeItem(key));
        setStateReady(true);
      } catch (error) {
        setToast(error.message || "No fue posible cargar Supabase.");
      } finally {
        setAuthChecking(false);
      }
    };
    load();
  }, []);
  useEffect(() => {
    if (!stateReady || currentUser?.role !== "ADMIN") return undefined;
    const timer = window.setTimeout(async () => {
      const response = await fetch("/api/v1/state/", {
        method: "PUT",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken(),
        },
        body: JSON.stringify({
          branches,
          inventories,
          suppliers,
          sales,
          users,
        }),
      });
      if (!response.ok)
        setToast("No se pudieron guardar los cambios en Supabase.");
    }, 600);
    return () => window.clearTimeout(timer);
  }, [stateReady, currentUser, branches, inventories, suppliers, sales, users]);
  useEffect(() => localStorage.setItem("pharma-branch", branchId), [branchId]);
  useEffect(() => {
    if (!toast) return undefined;
    const timer = window.setTimeout(() => setToast(""), 3200);
    return () => window.clearTimeout(timer);
  }, [toast]);
  if (authChecking)
    return <main className="auth-loading">Verificando sesión segura…</main>;
  if (!currentUser)
    return <CredentialLogin onLogin={() => window.location.reload()} />;
  if (!stateReady)
    return (
      <main className="auth-loading">
        <p>{toast || "No se pudieron preparar los datos del sistema."}</p>
        <button
          className="button primary"
          onClick={() => window.location.reload()}
        >
          Reintentar
        </button>
      </main>
    );
  if (!branches.length)
    return (
      <main className="auth-loading">
        <p>No hay una sucursal activa asignada a esta cuenta.</p>
        <button
          className="button primary"
          onClick={() => window.location.reload()}
        >
          Volver a comprobar
        </button>
      </main>
    );
  const items = inventories[branchId] || [],
    setItems = (next) => setInventories({ ...inventories, [branchId]: next }),
    branch = branches.find((b) => b.id === branchId) || branches[0];
  const saveNew = (m) => {
    setItems([...items, { ...m, id: Date.now() }]);
    setModal(false);
    setActive("Inventario");
  };
  return (
    <div className="app">
      <Sidebar
        active={active}
        setActive={setActive}
        open={sidebar}
        setOpen={setSidebar}
        user={currentUser}
      />
      <div className="workspace">
        <header className="topbar">
          <button className="menu-button" onClick={() => setSidebar(true)}>
            <Menu />
          </button>
          <select
            className="branch-select"
            value={branchId}
            onChange={(e) => setBranchId(e.target.value)}
          >
            {branches
              .filter(
                (b) =>
                  b.active !== false &&
                  (currentUser.role === "ADMIN" ||
                    currentUser.branchIds?.includes(b.id)),
              )
              .map((b) => (
                <option value={b.id} key={b.id}>
                  {b.name}
                </option>
              ))}
          </select>
          <button className="top-alert" onClick={() => setActive("Alertas")}>
            <Bell />
            <i>{items.filter((p) => p.stock <= p.min).length}</i>
          </button>
          <button
            className="button primary new-med"
            onClick={() => setModal(true)}
          >
            <Plus />
            Nuevo Medicamento
          </button>
          <button className="profile" onClick={() => setLogoutDialog(true)}>
            <img
              src="https://lh3.googleusercontent.com/a/default-user=s96-c"
              alt="Avatar de usuario"
            />
            <span>
              <b>{currentUser.name}</b>
              <small>
                {currentUser.role === "ADMIN"
                  ? "Administrador"
                  : "Encargado de inventario"}
              </small>
            </span>
            <ChevronDown />
          </button>
        </header>
        <main className="content">
          {active === "Dashboard" ? (
            <Dashboard
              items={items}
              branch={branch}
              user={currentUser}
              onInventory={() => setActive("Inventario")}
            />
          ) : active === "Inventario" ? (
            <Inventory
              items={items}
              setItems={setItems}
              branchId={branchId}
              initialQuery=""
              onAdd={() => setModal(true)}
            />
          ) : active === "Sucursales" ? (
            <BranchManager
              {...{
                branches,
                setBranches,
                inventories,
                setInventories,
                branchId,
                setBranchId,
              }}
            />
          ) : active === "Proveedores" ? (
            <Suppliers suppliers={suppliers} setSuppliers={setSuppliers} />
          ) : active === "Compras" ? (
            <Purchases branch={branch} items={items} suppliers={suppliers} />
          ) : active === "Caja" ? (
            <CashRegister branch={branch} />
          ) : active === "Transferencias" ? (
            <Transfers branch={branch} branches={branches} />
          ) : active === "Punto de Venta (POS)" ? (
            <Sales
              items={items}
              setItems={setItems}
              sales={sales}
              setSales={setSales}
              branch={branch}
            />
          ) : active === "Usuarios y Accesos" ? (
            <UserManagement
              users={users}
              setUsers={setUsers}
              branches={branches}
            />
          ) : active === "Reportes" ? (
            <AdminReports
              branches={branches}
              inventories={inventories}
              sales={sales}
              users={users}
              onNotify={setToast}
            />
          ) : (
            <Alerts
              items={items}
              setItems={setItems}
              branch={branch}
              lotAlerts={lotAlerts}
            />
          )}
        </main>
      </div>
      {modal && (
        <MedicineModal onClose={() => setModal(false)} onSave={saveNew} />
      )}
      {logoutDialog && (
        <ConfirmDialog
          icon={LogOut}
          eyebrow="SESIÓN ACTIVA"
          title="¿Quieres cerrar sesión?"
          message="Tu información guardada permanecerá disponible. Tendrás que ingresar nuevamente para continuar trabajando."
          confirmLabel="Cerrar sesión"
          tone="danger"
          onClose={() => setLogoutDialog(false)}
          onConfirm={async () => {
            const csrfToken = document.cookie
              .split("; ")
              .find((row) => row.startsWith("csrftoken="))
              ?.split("=")[1];
            await fetch("/api/v1/auth/logout/", {
              method: "POST",
              credentials: "same-origin",
              headers: { "X-CSRFToken": csrfToken || "" },
            });
            localStorage.removeItem("pharma-current-user");
            setLogoutDialog(false);
            setCurrentUser(null);
          }}
        />
      )}
      {toast && <SuccessToast message={toast} />}
    </div>
  );
}
