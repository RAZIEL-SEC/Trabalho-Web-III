export type MovementType = 'income' | 'outcome';
export type TipoMovimentacao = 'Entrada' | 'Saída';

export interface Movement {
  id: string;
  type: MovementType;
  occurredAt: string;
  itemName: string;
  quantity: number;
  unit: string;
  createdBy: string;
  notes?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface Movimentacao {
  id: string;
  tipo: TipoMovimentacao;
  data: string;
  item: string;
  quantidade: number;
  unidade: string;
  responsavel: string;
  observacoes?: string;
  criadoEm: string;
  atualizadoEm?: string;
  historico?: { acao: string; por: string; em: string }[];
}
