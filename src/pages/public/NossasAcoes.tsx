const acoes = [
  {
    icon: '🍱',
    titulo: 'Distribuição de Quentinhas',
    publico: 'Pessoas em situação de rua',
    desc: 'Toda semana preparamos e distribuímos refeições quentes para pessoas em situação de rua. A quentinha vai além do alimento — é um gesto de humanidade e presença.',
    img: 'https://images.unsplash.com/photo-1504754524776-8f4f37790ca0?w=500&h=300&fit=crop&auto=format',
    alt: 'Refeição quente sendo distribuída',
  },
  {
    icon: '🛒',
    titulo: 'Cestas Básicas',
    publico: 'Famílias em vulnerabilidade',
    desc: 'Entregamos cestas com alimentos essenciais para famílias cadastradas que enfrentam dificuldades. Cada cesta é montada com cuidado para atender as necessidades nutricionais básicas.',
    img: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500&h=300&fit=crop&auto=format',
    alt: 'Cesta básica com alimentos',
  },
  {
    icon: '🧴',
    titulo: 'Kits de Higiene',
    publico: 'Pessoas em situação de vulnerabilidade',
    desc: 'Distribuímos kits com produtos de higiene pessoal — sabonete, shampoo, pasta de dente, absorvente e outros itens essenciais que muitas vezes não são cobertos por doações de alimentos.',
    img: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500&h=300&fit=crop&auto=format',
    alt: 'Produtos de higiene organizados',
  },
  {
    icon: '👕',
    titulo: 'Campanhas de Roupas',
    publico: 'Comunidade em geral',
    desc: 'Realizamos campanhas de arrecadação de roupas, calçados e agasalhos, distribuindo-os para famílias e pessoas que precisam. Especialmente ativa no inverno, a campanha acolhe doações de toda a cidade.',
    img: 'https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=500&h=300&fit=crop&auto=format',
    alt: 'Roupas organizadas para doação',
  },
  {
    icon: '📚',
    titulo: 'Amigos da Escola',
    publico: 'Crianças e adolescentes',
    desc: 'O projeto Amigos da Escola oferece reforço escolar, apoio à alfabetização e atividades educativas para crianças de comunidades vulneráveis. Acreditamos que a educação é o caminho mais duradouro para a transformação social.',
    img: 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=500&h=300&fit=crop&auto=format',
    alt: 'Crianças estudando e aprendendo',
  },
];

export default function NossasAcoes() {
  return (
    <>
      <section className="bg-[#1a3a6e] text-white py-16 px-4">
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-blue-200 font-semibold uppercase tracking-widest text-xs mb-3">O que fazemos</p>
          <h1 className="font-serif text-4xl md:text-5xl font-bold mb-6">Nossas Ações</h1>
          <p className="text-white/80 text-lg leading-relaxed">
            Cada ação nasce da escuta da comunidade e do compromisso de agir onde a necessidade é maior.
          </p>
        </div>
      </section>

      <section className="max-w-5xl mx-auto px-4 py-16">
        <div className="space-y-16">
          {acoes.map((a, i) => (
            <div
              key={a.titulo}
              className={`grid md:grid-cols-2 gap-10 items-center ${i % 2 === 1 ? 'md:flex-row-reverse' : ''}`}
              style={{ direction: i % 2 === 1 ? 'rtl' : 'ltr' }}
            >
              <div style={{ direction: 'ltr' }}>
                <div className="text-4xl mb-4">{a.icon}</div>
                <span className="inline-block bg-[#ddeeff] text-[#1a3a6e] text-xs font-semibold px-3 py-1 rounded-full mb-3">
                  {a.publico}
                </span>
                <h2 className="font-serif text-2xl md:text-3xl font-bold text-[#1a3a6e] mb-4">{a.titulo}</h2>
                <p className="text-[#4a6080] leading-relaxed">{a.desc}</p>
              </div>
              <div className="rounded-2xl overflow-hidden shadow-lg" style={{ direction: 'ltr' }}>
                <img src={a.img} alt={a.alt} className="w-full h-64 object-cover" />
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-[#ddeeff] py-16 px-4 text-center">
        <h2 className="font-serif text-2xl md:text-3xl font-bold text-[#1a3a6e] mb-4">
          Você também pode fazer parte
        </h2>
        <p className="text-[#4a6080] max-w-lg mx-auto mb-8">
          Seja voluntário, doe alimentos ou contribua financeiramente. Cada gesto conta.
        </p>
        <a
          href="/como-ajudar"
          className="bg-[#1a3a6e] text-white font-bold px-8 py-3 rounded-md hover:bg-[#0f1f3d] transition-colors inline-block"
        >
          Como ajudar
        </a>
      </section>
    </>
  );
}
