export default function ComoAjudar() {
  return (
    <>
      <section className="bg-[#1a3a6e] text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-blue-200 font-semibold uppercase tracking-widest text-xs mb-3">Participe</p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-6">Como Ajudar</h1>
          <p className="text-white/80 text-lg leading-relaxed">
            Existem muitas formas de contribuir. Escolha a que faz mais sentido para você.
          </p>
        </div>
      </section>

      {/* Donation */}
      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <div className="text-4xl mb-4">🎁</div>
            <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-4">Doações de alimentos e itens</h2>
            <p className="text-[#4a6080] leading-relaxed mb-4">
              Aceitamos doações de alimentos não perecíveis, produtos de higiene pessoal, roupas em bom estado e materiais escolares. Sua doação vai diretamente para quem mais precisa.
            </p>
            <div className="bg-[#ddeeff] rounded-xl p-5 mb-4">
              <h3 className="font-bold text-[#1a3a6e] mb-2">Itens mais necessários</h3>
              <ul className="text-sm text-[#4a6080] space-y-1">
                <li>✔ Arroz, feijão, macarrão, óleo</li>
                <li>✔ Leite, açúcar, farinha</li>
                <li>✔ Sabonete, shampoo, pasta de dente</li>
                <li>✔ Absorventes, fraldas</li>
                <li>✔ Roupas limpas e em bom estado</li>
                <li>✔ Material escolar</li>
              </ul>
            </div>
            <p className="text-sm text-[#4a6080]">
              📍 Ponto de coleta: entre em contato conosco para saber os pontos de entrega disponíveis na sua região.
            </p>
          </div>
          <div className="rounded-2xl overflow-hidden shadow-lg">
            <img
              src="https://images.unsplash.com/photo-1547592180-85f173990554?w=600&h=420&fit=crop&auto=format"
              alt="Pessoas doando alimentos"
              className="w-full h-72 object-cover"
            />
          </div>
        </div>

        {/* Financial */}
        <div className="bg-[#1a3a6e] text-white rounded-2xl p-8 mb-12">
          <div className="flex flex-col md:flex-row md:items-center gap-6">
            <div className="text-5xl">💙</div>
            <div>
              <h2 className="font-serif text-2xl font-bold mb-3">Contribuição financeira</h2>
              <p className="text-white/80 leading-relaxed mb-4">
                Contribuições financeiras nos ajudam a comprar alimentos frescos, cobrir custos operacionais e ampliar nossas ações. Para saber como contribuir, entre em contato diretamente conosco.
              </p>
              <p className="text-sm text-white/60">
                Não realizamos transações financeiras por esta plataforma. Entre em contato pelo e-mail ou WhatsApp para mais informações sobre como fazer sua doação financeira com segurança.
              </p>
            </div>
          </div>
        </div>

        {/* Volunteer */}
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div className="rounded-2xl overflow-hidden shadow-lg">
            <img
              src="https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=600&h=420&fit=crop&auto=format"
              alt="Voluntários trabalhando juntos"
              className="w-full h-72 object-cover"
            />
          </div>
          <div>
            <div className="text-4xl mb-4">🤝</div>
            <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-4">Seja voluntário</h2>
            <p className="text-[#4a6080] leading-relaxed mb-4">
              Nosso trabalho é feito por pessoas como você. Se você tem disponibilidade para dedicar algumas horas por semana, pode fazer parte do nosso time de voluntários.
            </p>
            <p className="text-[#4a6080] leading-relaxed mb-6">
              Precisamos de voluntários para distribuição de alimentos, organização de campanhas, reforço escolar, comunicação e muito mais.
            </p>
            <a
              href="https://forms.google.com"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-[#1a3a6e] text-white font-bold px-8 py-3 rounded-md hover:bg-[#0f1f3d] transition-colors inline-block"
            >
              Quero ser voluntário
            </a>
            <p className="text-xs text-[#4a6080] mt-3">
              Você será redirecionado para o formulário de cadastro de voluntários.
            </p>
          </div>
        </div>
      </section>

      {/* Partnership */}
      <section className="bg-[#ddeeff] py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <div className="text-4xl mb-4">🏢</div>
          <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-4">Parcerias institucionais</h2>
          <p className="text-[#4a6080] leading-relaxed mb-6">
            Empresas, igrejas, associações de bairro e outras organizações podem se tornar parceiras dos Amigos do Zé Alguém. Entre em contato para conhecer as possibilidades de colaboração.
          </p>
          <a
            href="/contato"
            className="bg-[#1a3a6e] text-white font-bold px-8 py-3 rounded-md hover:bg-[#0f1f3d] transition-colors inline-block"
          >
            Fale conosco
          </a>
        </div>
      </section>
    </>
  );
}
