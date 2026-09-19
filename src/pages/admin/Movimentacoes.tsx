import { useState } from 'react';
import { Link } from 'react-router';
import { movimentacoesIniciais, Movimentacao, TipoMovimentacao } from '../../data/mockData';

export default function Movimentacoes() {
  const [dados, setDados] = useState<Movimentacao[]>(movimentacoesIniciais);
  const [busca, setBusca] = useState('');
  const [filtroTipo, setFiltroTipo] = useState<TipoMovimentacao | ''>('');

  const filtrados = dados.filter((m) => {
    const matchBusca =
      !busca ||
      m.item.toLowerCase().includes(busca.toLowerCase()) ||
      m.responsavel.toLowerCase().includes(busca.toLowerCase());
    const matchTipo = !filtroTipo || m.tipo === filtroTipo;
    return matchBusca && matchTipo;
  });

  return (
    <div>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-bold text-[#1a3a6e]">Movimentações</h1>
          <p className="text-sm text-[#4a6080]">{dados.length} registros no total</p>
        </div>
        <Link
          to="/admin/dashboard/registrar"
          className="inline-flex items-center gap-2 bg-[#1a3a6e] text-white font-bold px-5 py-2.5 rounded-md hover:bg-[#0f1f3d] transition-colors text-sm self-start sm:self-auto"
        >
          ➕ Registrar
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white border border-[#c8d8ef] rounded-xl p-4 mb-4 flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          placeholder="Buscar por item ou responsável..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          className="flex-1 border border-[#c8d8ef] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
        />
        <select
          value={filtroTipo}
          onChange={(e) => setFiltroTipo(e.target.value as TipoMovimentacao | '')}
          className="border border-[#c8d8ef] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#2d7dd2] bg-white"
        >
          <option value="">Todos os tipos</option>
          <option value="Entrada">Entrada</option>
          <option value="Saída">Saída</option>
        </select>
        {(busca || filtroTipo) && (
          <button
            onClick={() => { setBusca(''); setFiltroTipo(''); }}
            className="text-sm text-[#4a6080] hover:text-[#1a3a6e] transition-colors px-2"
          >
            Limpar filtros
          </button>
        )}
      </div>

      {/* Desktop table */}
      <div className="hidden md:block bg-white border border-[#c8d8ef] rounded-xl overflow-hidden">
        {filtrados.length === 0 ? (
          <div className="text-center py-16 text-[#4a6080]">
            <div className="text-4xl mb-3">🔍</div>
            <p className="font-semibold">Nenhum registro encontrado</p>
            <p className="text-sm mt-1">Tente ajustar os filtros ou a busca.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#c8d8ef] bg-[#f8faff]">
                <th className="px-4 py-3 text-left font-semibold text-[#4a6080]">Tipo</th>
                <th className="px-4 py-3 text-left font-semibold text-[#4a6080]">Data</th>
                <th className="px-4 py-3 text-left font-semibold text-[#4a6080]">Item</th>
                <th className="px-4 py-3 text-left font-semibold text-[#4a6080]">Qtde</th>
                <th className="px-4 py-3 text-left font-semibold text-[#4a6080]">Responsável</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#c8d8ef]">
              {filtrados.map((m) => (
                <tr key={m.id} className="hover:bg-[#f8faff] transition-colors">
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                        m.tipo === 'Entrada' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {m.tipo}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-[#4a6080] font-mono text-xs">{m.data}</td>
                  <td className="px-4 py-3 font-semibold text-[#1a3a6e]">{m.item}</td>
                  <td className="px-4 py-3 text-[#4a6080]">{m.quantidade} {m.unidade}</td>
                  <td className="px-4 py-3 text-[#4a6080] text-xs">{m.responsavel}</td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/admin/dashboard/movimentacoes/${m.id}`}
                      className="text-[#2d7dd2] text-xs hover:underline font-semibold"
                    >
                      Ver →
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Mobile cards */}
      <div className="md:hidden space-y-3">
        {filtrados.length === 0 ? (
          <div className="bg-white border border-[#c8d8ef] rounded-xl text-center py-12 text-[#4a6080]">
            <div className="text-3xl mb-2">🔍</div>
            <p className="font-semibold text-sm">Nenhum registro encontrado</p>
          </div>
        ) : (
          filtrados.map((m) => (
            <Link
              key={m.id}
              to={`/admin/dashboard/movimentacoes/${m.id}`}
              className="block bg-white border border-[#c8d8ef] rounded-xl p-4 hover:shadow-sm transition-shadow"
            >
              <div className="flex items-center justify-between mb-2">
                <span
                  className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                    m.tipo === 'Entrada' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-700'
                  }`}
                >
                  {m.tipo}
                </span>
                <span className="text-xs text-[#4a6080] font-mono">{m.data}</span>
              </div>
              <p className="font-semibold text-[#1a3a6e]">{m.item}</p>
              <p className="text-sm text-[#4a6080]">{m.quantidade} {m.unidade}</p>
              <p className="text-xs text-[#4a6080] mt-1">{m.responsavel}</p>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
