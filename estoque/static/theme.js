(() => {
  const KEY = "amigos-ze-aparencia";
  const picker = document.querySelector("[data-theme-picker]");
  const media = window.matchMedia("(prefers-color-scheme: dark)");

  function preference() {
    try {
      const saved = localStorage.getItem(KEY);
      return ["light", "dark", "system"].includes(saved) ? saved : "light";
    } catch {
      return "light";
    }
  }

  function apply(mode) {
    const effective = mode === "system" ? (media.matches ? "dark" : "light") : mode;
    document.documentElement.dataset.theme = effective;
    document.documentElement.style.colorScheme = effective;
    if (picker && picker.value !== mode) picker.value = mode;
  }

  let selected = preference();
  apply(selected);
  if (picker) {
    picker.value = selected;
    picker.addEventListener("change", () => {
      selected = picker.value;
      try { localStorage.setItem(KEY, selected); } catch {}
      apply(selected);
    });
  }
  media.addEventListener?.("change", () => {
    if (selected === "system") apply("system");
  });
})();