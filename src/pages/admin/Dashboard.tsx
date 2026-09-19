import { Link } from 'react-router';
import { movimentacoesIniciais, USUARIO_LOGADO } from '../../data/mockData';

export default function Dashboard() {
  const entradas = movimentacoesIniciais.filter((m) => m.tipo === 'Entrada').length;
  const saidas = movimentacoesIniciais.filter((m) => m.tipo === 'Saída').length;
  const recentes = movimentacoesIniciais.slice(0, 5);

  const hoje = new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' });

  return (
    <div>
      {/* Welcome */}
      <div className="mb-8">
        <p className="text-sm text-[#4a6080] mb-1">{hoje}</p>
        <h1 className="font-serif text-2xl md:text-3xl font-bold text-[#1a3a6e]">
          Bem-vinda, {USUARIO_LOGADO.nome.split(' ')[1]} 👋
        </h1>
        <p className="text-[#4a6080] mt-1">Aqui está um resumo das movimentações recentes.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Total de registros</p>
          <p className="font-serif text-4xl font-bold text-[#1a3a6e]">{movimentacoesIniciais.length}</p>
        </div>
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Entradas</p>
          <p className="font-serif text-4xl font-bold text-green-700">{entradas}</p>
        </div>
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Saídas</p>
          <p className="font-serif text-4xl font-bold text-red-600">{saidas}</p>
        </div>
      </div>

      {/* Quick action */}
      <div className="mb-8">
        <Link
          to="/admin/dashboard/registrar"
          className="inline-flex items-center gap-2 bg-[#1a3a6e] text-white font-bold px-6 py-3 rounded-md hover:bg-[#0f1f3d] transition-colors"
        >
          <span>➕</span> Registrar movimentação
        </Link>
      </div>

      {/* Recent */}
      <div className="bg-white rounded-xl border border-[#c8d8ef] overflow-hidden">
        <div className="px-6 py-4 border-b border-[#c8d8ef] flex items-center justify-between">
          <h2 className="font-bold text-[#1a3a6e]">Movimentações recentes</h2>
          <Link to="/admin/dashboard/movimentacoes" className="text-sm text-[#2d7dd2] hover:underline">
            Ver todas →
          </Link>
        </div>

        <div className="divide-y divide-[#c8d8ef]">
          {recentes.map((m) => (
            <Link
              key={m.id}
              to={`/admin/dashboard/movimentacoes/${m.id}`}
              className="flex items-center gap-4 px-6 py-4 hover:bg-[#f8faff] transition-colors"
            >
              <span
                className={`inline-block px-2 py-0.5 rounded-full text-xs font-bold shrink-0 ${
                  m.tipo === 'Entrada'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {m.tipo}
              </span>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-[#1a3a6e] text-sm truncate">{m.item}</p>
                <p className="text-xs text-[#4a6080]">{m.quantidade} {m.unidade} · {m.responsavel}</p>
              </div>
              <span className="text-xs text-[#4a6080] shrink-0">{m.data}</span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
