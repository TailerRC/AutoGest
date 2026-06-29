function confirmarEliminar(btnEl, opts = {}) {
  const form = btnEl.closest("form");
  if (!form) {
    console.error("confirmarEliminar: no se encontró un <form> padre.");
    return;
  }

  const overlay = document.getElementById("modal-confirm-overlay");
  const tituloEl = document.getElementById("modal-confirm-titulo");
  const mensajeEl = document.getElementById("modal-confirm-mensaje");
  const btnAceptar = document.getElementById("modal-confirm-aceptar");

  tituloEl.textContent = opts.titulo || "¿Eliminar registro?";

  const nombreHtml = opts.nombre
    ? ` <strong>${escapeHtml(opts.nombre)}</strong>`
    : "";
  mensajeEl.innerHTML =
    (opts.mensaje || "Esta acción no se puede deshacer.") + nombreHtml;

  overlay.classList.add("is-open");
  document.body.style.overflow = "hidden";

  // Limpia cualquier listener anterior y asigna uno nuevo
  btnAceptar.onclick = () => {
    cerrarModalConfirm();
    form.submit();
  };
}

function cerrarModalConfirm() {
  const overlay = document.getElementById("modal-confirm-overlay");
  overlay.classList.remove("is-open");
  document.body.style.overflow = "";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// Cerrar con click en el overlay (fuera de la caja) o con tecla Escape
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("modal-confirm-overlay");
  if (!overlay) return;

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) cerrarModalConfirm();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("is-open")) {
      cerrarModalConfirm();
    }
  });
});