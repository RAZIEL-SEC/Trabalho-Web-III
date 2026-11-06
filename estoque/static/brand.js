// Usa diretamente a arte original incorporada em logo.svg.
// Caminho absoluto para funcionar igualmente no login e em todas as telas internas.
(() => {
  const logoUrl = "/estoque/static/logo.svg";
  document.querySelectorAll("[data-logo]").forEach((slot) => {
    const imagem = document.createElement("img");
    imagem.src = logoUrl;
    imagem.alt = "";
    imagem.setAttribute("aria-hidden", "true");
    imagem.decoding = "async";
    imagem.loading = "eager";
    imagem.className = "logo-imagem";
    slot.replaceChildren(imagem);
  });
})();
