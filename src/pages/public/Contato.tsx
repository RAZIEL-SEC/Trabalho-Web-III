export default function Contato() {
  return (
    <>
      <section className="bg-[#1a3a6e] text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-blue-200 font-semibold uppercase tracking-widest text-xs mb-3">Fale com a gente</p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-6">Contato</h1>
          <p className="text-white/80 text-lg">
            Estamos disponíveis para tirar dúvidas, receber doações e conhecer novos parceiros.
          </p>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-6">Informações de contato</h2>

            <div className="space-y-6">
              <div className="flex gap-4 items-start">
                <div className="w-12 h-12 bg-[#ddeeff] rounded-xl flex items-center justify-center text-2xl shrink-0">📧</div>
                <div>
                  <h3 className="font-bold text-[#1a3a6e] mb-1">E-mail</h3>
                  <p className="text-[#4a6080]">contato@amigosdozealgem.org</p>
                  <p className="text-sm text-[#4a6080]">Respondemos em até 48 horas úteis</p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="w-12 h-12 bg-[#ddeeff] rounded-xl flex items-center justify-center text-2xl shrink-0">📱</div>
                <div>
                  <h3 className="font-bold text-[#1a3a6e] mb-1">WhatsApp</h3>
                  <p className="text-[#4a6080]">(11) 9 0000-0000</p>
                  <p className="text-sm text-[#4a6080]">Segunda a sexta, das 9h às 18h</p>
                </div>
              </div>

              <div className="flex gap-4 items-start">
                <div className="w-12 h-12 bg-[#ddeeff] rounded-xl flex items-center justify-center text-2xl shrink-0">📍</div>
                <div>
                  <h3 className="font-bold text-[#1a3a6e] mb-1">Localização</h3>
                  <p className="text-[#4a6080]">São Paulo — SP</p>
                  <p className="text-sm text-[#4a6080]">Entre em contato para saber os pontos de atendimento</p>
                </div>
              </div>
            </div>

            {/* Social media */}
            <div className="mt-10">
              <h3 className="font-bold text-[#1a3a6e] mb-4">Redes sociais</h3>
              <div className="flex gap-4">
                {[
                  { label: 'Instagram', icon: '📸', href: '#' },
                  { label: 'Facebook', icon: '📘', href: '#' },
                  { label: 'YouTube', icon: '▶️', href: '#' },
                ].map(({ label, icon, href }) => (
                  <a
                    key={label}
                    href={href}
                    className="flex flex-col items-center gap-1 bg-[#ddeeff] rounded-xl p-4 hover:bg-[#c8d8ef] transition-colors w-24"
                  >
                    <span className="text-2xl">{icon}</span>
                    <span className="text-xs font-semibold text-[#1a3a6e]">{label}</span>
                  </a>
                ))}
              </div>
            </div>
          </div>

          <div>
            <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-6">Envie uma mensagem</h2>
            <form
              className="space-y-4"
              onSubmit={(e) => {
                e.preventDefault();
                alert('Mensagem enviada! Entraremos em contato em breve.');
              }}
            >
              <div>
                <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Nome *</label>
                <input
                  type="text"
                  required
                  placeholder="Seu nome completo"
                  className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">E-mail *</label>
                <input
                  type="email"
                  required
                  placeholder="seu@email.com"
                  className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Assunto</label>
                <select className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white">
                  <option>Quero ser voluntário</option>
                  <option>Quero fazer uma doação</option>
                  <option>Parceria institucional</option>
                  <option>Dúvidas gerais</option>
                  <option>Outro</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#1a3a6e] mb-1">Mensagem *</label>
                <textarea
                  required
                  rows={5}
                  placeholder="Escreva sua mensagem aqui..."
                  className="w-full border border-[#c8d8ef] rounded-md px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white resize-none"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-[#1a3a6e] text-white font-bold py-3 rounded-md hover:bg-[#0f1f3d] transition-colors"
              >
                Enviar mensagem
              </button>
            </form>
          </div>
        </div>
      </section>
    </>
  );
}
