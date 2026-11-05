import fotoArrecadacaoRoupa from '@/imports/Foto_arrecadacao_roupa.jpg';
import fotoBalaoAmigos from '@/imports/Foto_balao_amigos_do_ze_alguem.jpg';
import fotoCestaBasica from '@/imports/Foto_cesta_basica-1.jpg';
import fotoDosParticipantes from '@/imports/Foto_dos_participantes.jpg';

const acoes = [
  {
    icon: '🍱',
    titulo: 'Distribuição de Quentinhas',
    publico: 'Pessoas em situação de rua',
    desc: 'Toda semana preparamos e distribuímos refeições quentes para pessoas em situação de rua. A quentinha vai além do alimento — é um gesto de humanidade e presença.',
    img: '/images/foto-distribuicao-quentinhas.jpg',
    alt: 'Quentinhas preparadas para distribuição',
  },
  {
    icon: '🛒',
    titulo: 'Cestas Básicas',
    publico: 'Famílias em vulnerabilidade',
    desc: 'Entregamos cestas com alimentos essenciais para famílias cadastradas que enfrentam dificuldades. Cada cesta é montada com cuidado para atender as necessidades nutricionais básicas.',
    img: fotoCestaBasica,
    alt: 'Voluntários dos Amigos do Zé Alguém diante de cestas básicas prontas para entrega',
  },
  {
    icon: '🧴',
    titulo: 'Kits de Higiene',
    publico: 'Pessoas em situação de vulnerabilidade',
    desc: 'Distribuímos kits com produtos de higiene pessoal — sabonete, shampoo, pasta de dente, absorvente e outros itens essenciais que muitas vezes não são cobertos por doações de alimentos.',
    img: fotoDosParticipantes,
    alt: 'Moradores e voluntários reunidos em uma ação comunitária',
  },
  {
    icon: '👕',
    titulo: 'Campanhas de Roupas',
    publico: 'Comunidade em geral',
    desc: 'Realizamos campanhas de arrecadação de roupas, calçados e agasalhos, distribuindo-os para famílias e pessoas que precisam. Especialmente ativa no inverno, a campanha acolhe doações de toda a cidade.',
    img: fotoArrecadacaoRoupa,
    alt: 'Kits de roupas arrecadados para doação',
  },
  {
    icon: '📚',
    titulo: 'Amigos da Escola',
    publico: 'Crianças e adolescentes',
    desc: 'O projeto Amigos da Escola oferece reforço escolar, apoio à alfabetização e atividades educativas para crianças de comunidades vulneráveis. Acreditamos que a educação é o caminho mais duradouro para a transformação social.',
    img: fotoBalaoAmigos,
    alt: 'Criança segura um balão dos Amigos do Zé Alguém durante uma ação',
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
