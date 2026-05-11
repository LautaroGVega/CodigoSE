(function () {
  const grid = document.getElementById("evidencias-grid");
  const out = document.getElementById("resultado-area");
  const panelOut = document.getElementById("panel-out");
  const hipotesisGrid = document.getElementById("hipotesis-grid");
  const evidenciasInfoGrid = document.getElementById("evidencias-info-grid");
  const reglasGlobales = document.getElementById("reglas-globales");

  function escapeHtml(s) {
    if (s === null || s === undefined) return "";
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function confClass(nivel) {
    const n = (nivel || "").toLowerCase();
    if (n.indexOf("alto") !== -1 && n.indexOf("incierto") === -1) return "conf-alto";
    if (n.indexOf("medio") !== -1) return "conf-medio";
    if (n.indexOf("bajo") !== -1 || n.indexOf("incierto") !== -1) return "conf-bajo";
    return "conf-incierto";
  }

  function barClass(h) {
    if (h === "H2") return "h2";
    if (h === "H3") return "h3";
    return "";
  }

  function setLoading(on) {
    panelOut.classList.toggle("loading", on);
  }

  function renderGuia(meta) {
    const hip = meta.hipotesis_descripciones || {};
    const evd = meta.evidencias_descripciones || {};

    hipotesisGrid.innerHTML = Object.keys(hip)
      .map(function (h) {
        const item = hip[h];
        const tags = (item.evidencias_clave || [])
          .map(function (ev) {
            return '<span class="tag">' + escapeHtml(ev) + "</span>";
          })
          .join("");
        return (
          '<div class="hyp-card"><h4>' +
          h +
          " · " +
          escapeHtml(item.titulo) +
          "</h4><p>" +
          escapeHtml(item.descripcion) +
          "</p>" +
          (tags ? '<div class="tag-list">' + tags + "</div>" : "") +
          "</div>"
        );
      })
      .join("");

    evidenciasInfoGrid.innerHTML = Object.keys(evd)
      .map(function (id) {
        const item = evd[id];
        const fav = (item.favorece || [])
          .map(function (h) {
            return '<span class="tag">' + escapeHtml(h) + "</span>";
          })
          .join("");
        return (
          '<div class="ev-card"><h4>' +
          escapeHtml(item.etiqueta) +
          "</h4><p>" +
          escapeHtml(item.descripcion) +
          '</p><div class="tag-list">' +
          fav +
          "</div></div>"
        );
      })
      .join("");

    reglasGlobales.innerHTML =
      "<li>menos de " +
      meta.min_evidencias +
      " evidencias => H4 evidencia insuficiente</li>" +
      "<li>diferencia menor a " +
      meta.umbral_incertidumbre +
      " => H4 diagnóstico incierto</li>" +
      "<li>diferencia mayor o igual a " +
      meta.umbral_confianza_alta +
      " => confianza alta</li>" +
      "<li>caso contrario => confianza media</li>";
  }

  function renderSeleccion(meta) {
    grid.innerHTML = "";
    (meta.evidencias || []).forEach(function (ev) {
      const div = document.createElement("div");
      div.className = "evid-item";
      const info = (meta.evidencias_descripciones || {})[ev.id] || {};
      const id = "ev-" + ev.id;
      div.innerHTML =
        '<input type="checkbox" id="' +
        id +
        '" value="' +
        ev.id +
        '">' +
        '<label for="' +
        id +
        '">' +
        escapeHtml(ev.etiqueta) +
        "<code>" +
        escapeHtml(ev.id) +
        "</code>" +
        (info.descripcion
          ? '<span style="display:block;color:#9aa8b8;font-size:.76rem;margin-top:3px">' +
            escapeHtml(info.descripcion) +
            "</span>"
          : "") +
        "</label>";
      grid.appendChild(div);
    });
  }

  function renderCaso(data) {
    if (!data.ok) {
      out.innerHTML =
        '<div class="empty-state">' +
        escapeHtml(data.error || "Error en análisis.") +
        "</div>";
      return;
    }
    const r = data;
    const pills =
      '<span class="conf-pill ' +
      confClass(r.nivel_confianza) +
      '">' +
      escapeHtml(r.nivel_confianza) +
      "</span>";
    let rules = '<ul class="rules">';
    (r.reglas_activadas || []).forEach(function (reg) {
      rules +=
        "<li><strong>" +
        escapeHtml(reg.codigo) +
        "</strong> — " +
        escapeHtml(reg.explicacion) +
        "</li>";
    });
    rules += "</ul>";
    let bars = '<div class="bars">';
    (r.ranking || []).forEach(function (row) {
      const pct = row.porcentaje;
      bars +=
        '<div class="bar-row"><span>' +
        escapeHtml(row.hipotesis) +
        '</span><div class="bar-track"><div class="bar-fill ' +
        barClass(row.hipotesis) +
        '" style="width:' +
        pct +
        '%"></div></div><span>' +
        pct.toFixed(2) +
        "%</span></div>";
    });
    bars += "</div>";
    let razon = "";
    if (r.razonamiento_aplicado) {
      const rz = r.razonamiento_aplicado;
      const priors = rz.priors || {};
      const priorsTxt =
        "H1=" +
        ((priors.H1 || 0) * 100).toFixed(2) +
        "%, H2=" +
        ((priors.H2 || 0) * 100).toFixed(2) +
        "%, H3=" +
        ((priors.H3 || 0) * 100).toFixed(2) +
        "%";
      razon =
        '<div class="razonamiento"><strong>Razonamiento aplicado</strong>' +
        "<ul>" +
        "<li>Cantidad de evidencias seleccionadas: " +
        rz.cantidad_evidencias +
        "</li>" +
        "<li>Método usado: " +
        escapeHtml(rz.metodo) +
        "</li>" +
        "<li>Priors utilizados: " +
        escapeHtml(priorsTxt) +
        "</li>" +
        "<li>Diferencia entre primera y segunda hipótesis: " +
        Number(rz.diferencia_porcentaje).toFixed(2) +
        "%</li>" +
        (rz.criterios || [])
          .map(function (c) {
            return "<li>Criterio: " + escapeHtml(c) + "</li>";
          })
          .join("") +
        "<li><strong>" +
        escapeHtml(rz.conclusion) +
        "</strong></li>" +
        "</ul></div>";
    }
    let val = r.validacion
      ? '<div class="val-box"><strong>Validación:</strong> ' +
        escapeHtml(r.validacion) +
        "</div>"
      : "";
    out.innerHTML =
      '<div class="result-header"><div class="diag-box"><strong>Diagnóstico:</strong> ' +
      escapeHtml(r.diagnostico_texto) +
      "</div>" +
      pills +
      "</div>" +
      '<p style="margin:0 0 8px;color:#9aa8b8;font-size:.84rem"><strong>Caso:</strong> ' +
      escapeHtml(r.nombre_caso) +
      "</p>" +
      bars +
      '<p style="margin:14px 0 6px;font-size:.88rem;color:#9aa8b8"><strong>Reglas activadas</strong></p>' +
      rules +
      razon +
      '<div class="reco"><strong>Recomendación</strong><br>' +
      escapeHtml(r.recomendacion) +
      "</div>" +
      val;
  }

  function evidenciasSeleccionadas() {
    const boxes = grid.querySelectorAll("input[type=checkbox]:checked");
    return Array.prototype.map.call(boxes, function (c) {
      return c.value;
    });
  }

  async function postAnalizar(body) {
    setLoading(true);
    try {
      const res = await fetch("/api/analizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      renderCaso(data);
    } catch (e) {
      out.innerHTML =
        '<div class="empty-state">No se pudo conectar al servidor.</div>';
    } finally {
      setLoading(false);
    }
  }

  document.getElementById("btn-analizar").addEventListener("click", function () {
    const ev = evidenciasSeleccionadas();
    if (!ev.length) {
      out.innerHTML =
        '<div class="empty-state">Selecciona al menos una evidencia.</div>';
      return;
    }
    postAnalizar({ evidencias: ev, nombre_caso: "Caso manual", esperado: null });
  });

  document.getElementById("btn-limpiar").addEventListener("click", function () {
    grid.querySelectorAll("input[type=checkbox]").forEach(function (c) {
      c.checked = false;
    });
    out.innerHTML =
      '<div class="empty-state">Selecciona evidencias y pulsa <strong>Analizar selección</strong>.</div>';
  });

  document.querySelectorAll("[data-caso]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const id = parseInt(btn.getAttribute("data-caso"), 10);
      fetch("/api/caso/" + id)
        .then(function (r) {
          return r.json();
        })
        .then(renderCaso);
    });
  });

  document.getElementById("btn-prop").addEventListener("click", async function () {
    setLoading(true);
    try {
      const res = await fetch("/api/propagacion");
      const data = await res.json();
      let html = "";
      (data.etapas || []).forEach(function (st) {
        html +=
          '<div class="prop-stage"><h3 style="margin:0 0 8px;font-size:.95rem">' +
          escapeHtml(st.nombre_caso) +
          "</h3>";
        html +=
          '<p style="margin:0 0 12px;font-size:.8rem;color:#9aa8b8">Evidencias: ' +
          (st.evidencias_detalle || [])
            .map(function (x) {
              return x.etiqueta;
            })
            .join(", ") +
          "</p>";
        const rr = st.resultado;
        html +=
          '<div class="result-header"><div class="diag-box" style="font-size:.85rem"><strong>Diagnóstico:</strong> ' +
          escapeHtml(rr.diagnostico_texto) +
          '</div><span class="conf-pill ' +
          confClass(rr.nivel_confianza) +
          '">' +
          escapeHtml(rr.nivel_confianza) +
          '</span></div><div class="bars">';
        (rr.ranking || []).forEach(function (row) {
          const pct = row.porcentaje;
          html +=
            '<div class="bar-row"><span>' +
            escapeHtml(row.hipotesis) +
            '</span><div class="bar-track"><div class="bar-fill ' +
            barClass(row.hipotesis) +
            '" style="width:' +
            pct +
            '%"></div></div><span>' +
            pct.toFixed(2) +
            "%</span></div>";
        });
        html += "</div></div>";
      });
      out.innerHTML = html || '<div class="empty-state">Sin datos.</div>';
    } catch (e) {
      out.innerHTML =
        '<div class="empty-state">Error al cargar propagación.</div>';
    } finally {
      setLoading(false);
    }
  });

  fetch("/api/meta")
    .then(function (res) {
      return res.json();
    })
    .then(function (meta) {
      renderGuia(meta);
      renderSeleccion(meta);
    })
    .catch(function () {
      grid.innerHTML =
        '<div class="empty-state">No se pudo cargar /api/meta</div>';
      hipotesisGrid.innerHTML = '<div class="empty-state">Sin datos</div>';
      evidenciasInfoGrid.innerHTML = '<div class="empty-state">Sin datos</div>';
    });
})();
