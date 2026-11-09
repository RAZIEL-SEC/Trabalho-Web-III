// Aplica o tema antes de o navegador renderizar a página, evitando flash claro no modo escuro.
(() => {
  let mode = "light";
  try {
    const saved = localStorage.getItem("amigos-ze-aparencia");
    if (["light", "dark", "system"].includes(saved)) mode = saved;
  } catch {}

  const effective = mode === "system"
    ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
    : mode;

  document.documentElement.dataset.theme = effective;
  document.documentElement.style.colorScheme = effective;
})();
