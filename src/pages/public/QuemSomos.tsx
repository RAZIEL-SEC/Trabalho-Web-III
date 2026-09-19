const valores = [
  { n: 1, nome: 'Humanização', desc: 'Tratamos cada pessoa com dignidade e respeito, reconhecendo sua humanidade acima de qualquer circunstância.' },
  { n: 2, nome: 'Geração de Renda', desc: 'Apoiamos iniciativas que criam oportunidades de trabalho e autonomia financeira.' },
  { n: 3, nome: 'Cidadania', desc: 'Promovemos o exercício pleno dos direitos e deveres de cada indivíduo.' },
  { n: 4, nome: 'Vínculo Familiar', desc: 'Fortalecemos os laços familiares como base para a estabilidade e o bem-estar.' },
  { n: 5, nome: 'Direito à Moradia Digna', desc: 'Lutamos pelo acesso a um lar seguro e adequado para todas as famílias.' },
  { n: 6, nome: 'Acesso à Saúde', desc: 'Facilitamos o acesso a serviços de saúde física e mental para quem mais precisa.' },
  { n: 7, nome: 'Segurança Alimentar', desc: 'Garantimos que nenhuma pessoa durma com fome na nossa comunidade.' },
  { n: 8, nome: 'Conscientização', desc: 'Educamos e sensibilizamos a sociedade sobre as causas e consequências da vulnerabilidade social.' },
  { n: 9, nome: 'Direito à Educação', desc: 'Incentivamos o acesso ao conhecimento como caminho para a transformação social.' },
];

export default function QuemSomos() {
  return (
    <>
      {/* Hero */}
      <section className="bg-[#1a3a6e] text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-blue-200 font-semibold uppercase tracking-widest text-xs mb-3">Nossa história</p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-6">Quem Somos</h1>
          <p className="text-white/80 text-lg leading-relaxed">
            Nascemos da indignação de um grupo de amigos diante da realidade da fome no Brasil — e da certeza de que podemos fazer diferença.
          </p>
        </div>
      </section>

      {/* Story */}
      <section className="max-w-4xl mx-auto px-4 py-16">
        <div className="grid md:grid-cols-2 gap-12 items-center mb-16">
          <div>
            <h2 className="font-serif text-2xl font-bold text-[#1a3a6e] mb-4">Nossa história</h2>
            <p className="text-[#4a6080] leading-relaxed mb-4">
              Os Amigos do Zé Alguém surgiram de um encontro simples: um grupo de vizinhos que decidiu transformar preocupação em ação. O nome homenageia aquele que muitas vezes é invisível — o "zé alguém" que caminha pelas ruas sem que ninguém o veja.
            </p>
            <p className="text-[#4a6080] leading-relaxed mb-4">
              O que começou como uma distribuição de refeições no fim de semana tornou-se uma organização estruturada, com voluntários dedicados, parceiros institucionais e um compromisso cada vez mais amplo com a transformação social.
            </p>
            <p className="text-[#4a6080] leading-relaxed">
              Hoje atuamos em várias frentes: alimentação, educação, saúde e geração de renda — sempre com o mesmo espírito comunitário que nos deu origem.
            </p>
          </div>
          <div className="rounded-2xl overflow-hidden shadow-lg">
            <img
              src="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=600&h=420&fit=crop&auto=format"
              alt="Voluntários trabalhando juntos na comunidade"
              className="w-full h-72 object-cover"
            />
          </div>
        </div>

        {/* Mission & Vision */}
        <div className="grid md:grid-cols-2 gap-6 mb-16">
          <div className="bg-[#ddeeff] rounded-xl p-8">
            <div className="text-3xl mb-3">🎯</div>
            <h3 className="font-serif font-bold text-[#1a3a6e] text-xl mb-3">Missão</h3>
            <p className="text-[#4a6080] leading-relaxed">
              Combater a fome e a vulnerabilidade social por meio de ações coletivas, solidárias e sustentáveis, respeitando a dignidade de cada pessoa atendida.
            </p>
          </div>
          <div className="bg-[#1a3a6e] rounded-xl p-8 text-white">
            <div className="text-3xl mb-3">🌟</div>
            <h3 className="font-serif font-bold text-xl mb-3">Visão</h3>
            <p className="text-white/80 leading-relaxed">
              Um Brasil onde nenhuma pessoa precise dormir com fome, e onde cada comunidade tenha os recursos e o apoio necessários para se desenvolver com autonomia.
            </p>
          </div>
        </div>
      </section>

      {/* Values / Mandala */}
      <section className="bg-[#f8faff] py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <p className="text-[#2d7dd2] font-semibold uppercase tracking-widest text-xs mb-3">Nossos pilares</p>
            <h2 className="font-serif text-3xl md:text-4xl font-bold text-[#1a3a6e] mb-4">Mandala Social</h2>
            <p className="text-[#4a6080] max-w-xl mx-auto">
              Nove valores que orientam cada decisão, cada ação e cada relação que construímos.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {valores.map((v) => (
              <div key={v.n} className="bg-white rounded-xl p-6 border border-[#c8d8ef] hover:shadow-md transition-shadow flex gap-4">
                <div className="w-12 h-12 rounded-full bg-[#1a3a6e] flex items-center justify-center text-white font-bold text-lg shrink-0">
                  {v.n}
                </div>
                <div>
                  <h3 className="font-bold text-[#1a3a6e] mb-1">{v.nome}</h3>
                  <p className="text-sm text-[#4a6080] leading-relaxed">{v.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
