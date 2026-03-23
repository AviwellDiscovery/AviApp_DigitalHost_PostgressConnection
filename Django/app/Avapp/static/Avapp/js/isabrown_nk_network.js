(function () {
  function onReady(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  onReady(function () {
    var container = document.getElementById("nkNetworkContainer");
    if (!container) return;
    if (typeof window.cytoscape !== "function") return;

    var omicsChoice = document.getElementById("omicsChoice");
    var variableInput = document.getElementById("bacteriaSearch");
    var filterBtn = document.getElementById("filterTableButton");
    var seedInfo = document.getElementById("nk_seed_info_text");
    var plotlySunburstView = document.getElementById("plotlySunburstView");

    var topk = document.getElementById("nk_topk");
    var kn = document.getElementById("nk_kn");
    var absthr = document.getElementById("nk_absthr");
    var accmin = document.getElementById("nk_accmin");
    var topkVal = document.getElementById("nk_topk_val");
    var knVal = document.getElementById("nk_kn_val");
    var absthrVal = document.getElementById("nk_absthr_val");
    var accminVal = document.getElementById("nk_accmin_val");

    var buildBtn = document.getElementById("nk_build_btn");
    var highlightBtn = document.getElementById("nk_highlight_btn");
    var toggleLabelsBtn = document.getElementById("nk_toggle_labels_btn");
    var searchNode = document.getElementById("nk_search_node");

    var loading = document.getElementById("nk_loading");
    var cyContainer = document.getElementById("nk_cytoscape_container");
    var legend = document.getElementById("nk_legend");
    var stats = document.getElementById("nk_network_stats");
    var nodesCount = document.getElementById("nk_nodes_count");
    var edgesCount = document.getElementById("nk_edges_count");

    var cy = null;
    var labelsVisible = true;
    var resizeObserver = null;

    function stabilizeCanvas() {
      if (!cy) return;
      // Just resize and fit, don't modify container dimensions
      setTimeout(function () {
        if (!cy) return;
        cy.resize();
        cy.fit(cy.elements(), 40);
      }, 100);
    }

    function parseJsonResponse(resp) {
      return resp.text().then(function (txt) {
        var raw = (txt || "").trim();
        try {
          return { ok: resp.ok, status: resp.status, data: raw ? JSON.parse(raw) : {} };
        } catch (e) {
          var preview = raw.slice(0, 220).replace(/\n/g, " ");
          throw new Error("HTTP " + resp.status + " non-JSON response: " + preview);
        }
      });
    }

    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i += 1) {
          var cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }

    function csrfToken() {
      return getCookie("csrftoken") ||
        (document.querySelector("input[name='csrfmiddlewaretoken']") || {}).value ||
        "";
    }

    var pathPrefix = (function () {
      var p = window.location.pathname || "";
      var marker = "/isabrownv2/";
      var idx = p.indexOf(marker);
      if (idx === -1) return "";
      var prefix = p.slice(0, idx);
      return prefix.endsWith("/") ? prefix.slice(0, -1) : prefix;
    })();

    function getPageSeedTissue() {
      var p = (window.location.pathname || "").toLowerCase();
      if (p.indexOf("/isabrownv2/bacterien/") !== -1 || p.indexOf("/isabrownv2/bacterien2/") !== -1) return "otu";
      if (p.indexOf("/isabrownv2/muscle/") !== -1) return "muscle";
      if (p.indexOf("/isabrownv2/liver/") !== -1) return "liver";
      if (p.indexOf("/isabrownv2/molecule/") !== -1) return "metab";
      if (p.indexOf("/isabrownv2/fonctionnel/") !== -1 || p.indexOf("/isabrownv2/functionnal/") !== -1) return "metab";
      if (p.indexOf("/isabrownv2/scfa/") !== -1) return "metab";
      if (p.indexOf("/isabrownv2/ileum/") !== -1) return "ileum";
      return "ileum";
    }

    var pageSeedTissue = getPageSeedTissue();

    function currentSeed() {
      var variable = variableInput ? String(variableInput.value || "").trim() : "";
      if (!variable) return null;
      return { tissue: pageSeedTissue, id: variable };
    }

    function updateSeedInfo() {
      if (!seedInfo) return;
      var seed = currentSeed();
      if (!seed) {
        seedInfo.textContent = "Waiting for variable selection...";
      } else {
        seedInfo.textContent = seed.tissue + "::" + seed.id;
      }
    }

    function hasOmicsSelection() {
      return omicsChoice ? String(omicsChoice.value || "").trim() !== "" : true;
    }

    function toggleSection() {
      container.style.display = (currentSeed() && hasOmicsSelection()) ? "block" : "none";
      updateSeedInfo();
    }

    function getAllowedTissues() {
      var out = [];
      document.querySelectorAll(".nk-allowed-tissue:checked").forEach(function (cb) { out.push(cb.value); });
      return out;
    }

    function setSliderBindings() {
      if (topk && topkVal) topk.addEventListener("input", function () { topkVal.textContent = topk.value; });
      if (kn && knVal) kn.addEventListener("input", function () { knVal.textContent = kn.value; });
      if (absthr && absthrVal) absthr.addEventListener("input", function () { absthrVal.textContent = absthr.value; });
      if (accmin && accminVal) accmin.addEventListener("input", function () { accminVal.textContent = accmin.value; });
    }

    function buildNetwork() {
      var seed = currentSeed();
      if (!seed) {
        alert("Please select Omic and variable first.");
        return;
      }

      var allowed = getAllowedTissues();
      if (!allowed.length) {
        alert("Please select at least one allowed tissue.");
        return;
      }

      if (loading) loading.style.display = "block";
      if (cyContainer) cyContainer.style.display = "none";
      if (stats) stats.style.display = "none";

      var formData = new FormData();
      formData.append("seed_tissue", seed.tissue);
      formData.append("seed_id", seed.id);
      formData.append("top_k", topk ? parseInt(topk.value, 10) : 5);
      formData.append("kn", kn ? parseInt(kn.value, 10) : 3);
      formData.append("abs_thr", absthr ? parseFloat(absthr.value) : 0);
      formData.append("acc_min", accmin ? parseFloat(accmin.value) : 0);
      formData.append("layout", document.getElementById("nk_layout") ? document.getElementById("nk_layout").value : "cose");
      allowed.forEach(function (t) { formData.append("allowed_tissues[]", t); });

      fetch(pathPrefix + "/nk-network/build-graph/", {
        method: "POST",
        body: formData,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": csrfToken()
        },
        credentials: "same-origin"
      })
        .then(parseJsonResponse)
        .then(function (payload) {
          var data = payload.data || {};
          if (data.error) throw new Error(data.error);

          if (loading) loading.style.display = "none";
          if (cyContainer) cyContainer.style.display = "block";
          if (legend) legend.style.display = "block";
          if (stats) stats.style.display = "block";
          if (nodesCount && data.stats) nodesCount.textContent = data.stats.nodes;
          if (edgesCount && data.stats) edgesCount.textContent = data.stats.edges;

          // Small delay to ensure container is rendered before Cytoscape initializes
          setTimeout(function () {
            if (cy) { cy.destroy(); cy = null; }
            cy = window.cytoscape({
              container: cyContainer,
            elements: data.elements,
            style: data.stylesheet,
            layout: data.layout,
            pixelRatio: 1,
            textureOnViewport: false,
            hideEdgesOnViewport: false
          });
          cy.ready(function () {
            setTimeout(function () {
              if (!cy) return;
              stabilizeCanvas();
              if (!labelsVisible) {
                cy.style().selector("node").style("text-opacity", 0).update();
              }
            }, 80);
          });

          if (typeof ResizeObserver !== "undefined" && cyContainer) {
            if (resizeObserver) resizeObserver.disconnect();
            resizeObserver = new ResizeObserver(function () {
              if (!cy) return;
              stabilizeCanvas();
            });
            resizeObserver.observe(cyContainer);
          }

          window.addEventListener("resize", stabilizeCanvas, { passive: true });
          }); // End of setTimeout wrapper
        })
        .catch(function (err) {
          if (loading) loading.style.display = "none";
          alert("Failed to build network: " + err.message);
        });
    }

    setSliderBindings();

    // Enforce order: Sunburst MOFA-CC first, NK Network below it.
    if (plotlySunburstView && plotlySunburstView.parentNode) {
      plotlySunburstView.insertAdjacentElement("afterend", container);
    }

    toggleSection();
    window.updateNkSeedInfo = updateSeedInfo;

    if (omicsChoice) omicsChoice.addEventListener("change", toggleSection);
    if (variableInput) {
      variableInput.addEventListener("input", toggleSection);
      variableInput.addEventListener("change", toggleSection);
      variableInput.addEventListener("blur", toggleSection);
    }
    if (filterBtn) filterBtn.addEventListener("click", toggleSection);

    if (buildBtn) buildBtn.addEventListener("click", buildNetwork);

    if (toggleLabelsBtn) {
      toggleLabelsBtn.addEventListener("click", function () {
        labelsVisible = !labelsVisible;
        toggleLabelsBtn.textContent = labelsVisible ? "Hide Names" : "Show Names";
        if (!cy) return;
        cy.style()
          .selector("node")
          .style("label", "data(label)")
          .style("text-opacity", labelsVisible ? 0.95 : 0)
          .update();
      });
    }

    if (highlightBtn) {
      highlightBtn.addEventListener("click", function () {
        if (!cy) return;
        var nodeId = searchNode ? String(searchNode.value || "").trim() : "";
        if (!nodeId) { alert("Please enter a node ID (format: tissue::id)"); return; }
        var node = cy.getElementById(nodeId);
        if (!node || node.length === 0) { alert("Node not found: " + nodeId); return; }

        cy.elements().removeClass("highlight dim");
        var neighbors = node.neighborhood();
        cy.elements().addClass("dim");
        node.removeClass("dim");
        neighbors.removeClass("dim");
        node.addClass("highlight");
        cy.fit(node, 50);
      });
    }
  });
})();
