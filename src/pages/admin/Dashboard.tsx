import { Link } from 'react-router';

export default function Dashboard() {
  return (
    <div>
      {/* Welcome */}
      <div className="mb-8">
        <p className="text-sm text-[#4a6080] mb-1">{'{createdAt}'}</p>
        <h1 className="font-serif text-2xl md:text-3xl font-bold text-[#1a3a6e]">
          Bem-vinda, {'{userName}'} 👋
        </h1>
        <p className="text-[#4a6080] mt-1">Resumo de {'{movementList}'}.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Total de registros</p>
          <p className="font-serif text-4xl font-bold text-[#1a3a6e]">{'{recordCount}'}</p>
        </div>
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Entradas</p>
          <p className="font-serif text-4xl font-bold text-green-700">{'{incomeCount}'}</p>
        </div>
        <div className="bg-white rounded-xl border border-[#c8d8ef] p-6">
          <p className="text-xs text-[#4a6080] uppercase tracking-widest mb-1">Saídas</p>
          <p className="font-serif text-4xl font-bold text-red-600">{'{outcomeCount}'}</p>
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

        <div className="px-6 py-10 text-center text-sm text-[#4a6080]">{'{movementList}'}</div>
      </div>
    </div>
  );
}
