/**
 * Tipos espelhando 1:1 os schemas Pydantic do backend (app/schemas/*.py).
 * Nenhum tipo aqui deve "inventar" um formato diferente do que a API
 * realmente devolve - se o backend mudar um schema, este arquivo deve
 * mudar junto (não há geração automática nesta versão do projeto).
 */

// --- app/models/usuario.py:Papel -------------------------------------------
export type Papel = 'diretor' | 'coordenador' | 'professor' | 'aluno'

export const PAPEIS_ORDEM: Papel[] = ['diretor', 'coordenador', 'professor', 'aluno']

export const PAPEL_LABEL: Record<Papel, string> = {
  diretor: 'Diretor',
  coordenador: 'Coordenador',
  professor: 'Professor',
  aluno: 'Aluno',
}

/** Papéis que um usuário do `papel` dado pode criar (estritamente abaixo
 * na hierarquia) - espelha app/core/rbac.py:papeis_a_partir_de usado ao
 * inverso em app/services/usuario_service.py. */
export function papeisCriaveisPor(papel: Papel): Papel[] {
  const idx = PAPEIS_ORDEM.indexOf(papel)
  return PAPEIS_ORDEM.slice(idx + 1)
}

export function papelAtendeMinimo(papel: Papel, minimo: Papel): boolean {
  return PAPEIS_ORDEM.indexOf(papel) <= PAPEIS_ORDEM.indexOf(minimo)
}

// --- app/schemas/auth.py -----------------------------------------------
export interface UsuarioPublico {
  id: string
  nome: string
  email: string
  papel: Papel
  instituicao_id: string
  is_active: boolean
  created_at: string
}

export interface RegistroAlunoRequest {
  nome: string
  email: string
  senha: string
  instituicao_codigo: string
  aceite_lgpd: boolean
}

export interface LoginRequest {
  email: string
  senha: string
}

export interface TokenResponse {
  access_token: string
  access_token_expires_at: string
  refresh_token: string
  refresh_token_expires_at: string
  token_type: string
}

export interface ForgotPasswordResponse {
  message: string
  reset_token: string | null
}

// --- app/schemas/usuarios.py ---------------------------------------------
export interface CriarUsuarioRequest {
  nome: string
  email: string
  senha: string
  papel: Papel
}

// --- app/schemas/perfis.py -----------------------------------------------
export interface CondicaoPublica {
  id: string
  codigo: string
  nome: string
  descricao: string | null
}

export interface RegistrarPerfilAlunoRequest {
  condicoes_codigos: string[]
  observacoes: string | null
  aceite_consentimento: boolean
}

export interface PerfilAlunoResponse {
  id: string
  aluno_id: string
  versao: number
  observacoes: string | null
  criado_por_id: string
  criado_em: string
  condicoes: CondicaoPublica[]
}

export interface QuestaoTIPI {
  ordem: number
  texto: string
}

export interface BigFiveRespostasRequest {
  respostas: number[]
}

export interface BigFiveScores {
  abertura: number
  conscienciosidade: number
  extroversao: number
  amabilidade: number
  neuroticismo: number
}

export interface PerfilBigFiveResponse {
  id: string
  aluno_id: string
  versao: number
  criado_em: string
  scores: BigFiveScores
  instrumento: string
}

export type TamanhoFonte = 'pequeno' | 'medio' | 'grande' | 'extra_grande'

export interface PreferenciasAcessibilidadeRequest {
  fonte_legivel: boolean
  alto_contraste: boolean
  tempo_extra_percentual: number
  leitura_voz_alta: boolean
  reducao_estimulos: boolean
  tamanho_fonte: TamanhoFonte
}

export interface PreferenciasAcessibilidadeResponse extends PreferenciasAcessibilidadeRequest {
  usuario_id: string
}

// --- app/schemas/turmas.py -----------------------------------------------
export interface CriarTurmaRequest {
  nome: string
  periodo: string
  professor_responsavel_id: string
}

export interface TurmaResponse {
  id: string
  instituicao_id: string
  nome: string
  periodo: string
  professor_responsavel_id: string
  ativo: boolean
  created_at: string
}

export interface TurmaDetalheResponse extends TurmaResponse {
  total_professores: number
  total_alunos_ativos: number
}

export interface MatriculaResponse {
  id: string
  turma_id: string
  aluno_id: string
  aluno_nome: string
  aluno_email: string
  ativo: boolean
  matriculado_em: string
  desmatriculado_em: string | null
}

export interface ProgressoAlunoResponse {
  aluno_id: string
  aluno_nome: string
  problemas_resolvidos: number
  tentativas: number
  tempo_gasto_minutos: number
}

// --- app/models/problema.py / app/schemas/problemas.py -------------------
export type NivelDificuldade = 'facil' | 'medio' | 'dificil'
export type CategoriaTag = 'tema' | 'raciocinio'
export type StatusSubmissao =
  | 'aceito'
  | 'reprovado'
  | 'erro_execucao'
  | 'tempo_excedido'
  | 'erro_interno'

export const NIVEL_DIFICULDADE_LABEL: Record<NivelDificuldade, string> = {
  facil: 'Fácil',
  medio: 'Médio',
  dificil: 'Difícil',
}

export const STATUS_SUBMISSAO_LABEL: Record<StatusSubmissao, string> = {
  aceito: 'Aceito',
  reprovado: 'Reprovado',
  erro_execucao: 'Erro de execução',
  tempo_excedido: 'Tempo excedido',
  erro_interno: 'Erro interno',
}

export interface TagPublica {
  id: string
  categoria: CategoriaTag
  codigo: string
  nome: string
  descricao: string | null
}

export interface CasoTesteInputSchema {
  entrada: string
  saida_esperada: string
  publico: boolean
}

export interface CriarProblemaRequest {
  titulo: string
  enunciado: string
  linguagem: string
  nivel_dificuldade: NivelDificuldade
  tags_codigos: string[]
  casos: CasoTesteInputSchema[]
}

export interface CasoTesteResponse {
  id: string
  entrada: string
  saida_esperada: string
  publico: boolean
  ordem: number
}

export interface ProblemaResponse {
  id: string
  instituicao_id: string
  titulo: string
  enunciado: string
  linguagem: string
  nivel_dificuldade: NivelDificuldade
  criado_por_id: string
  ativo: boolean
  created_at: string
  tags: TagPublica[]
}

export interface ProblemaDetalheResponse extends ProblemaResponse {
  casos: CasoTesteResponse[]
}

export interface SubmeterCodigoRequest {
  codigo_fonte: string
}

export interface ResultadoCasoResponse {
  caso_teste_id: string
  publico: boolean
  passou: boolean
  tempo_execucao_ms: number
  entrada: string | null
  saida_esperada: string | null
  saida_obtida: string | null
  erro: string | null
}

export interface SubmissaoResponse {
  id: string
  problema_id: string
  aluno_id: string
  status: StatusSubmissao
  tempo_execucao_ms: number
  criado_em: string
  resultados: ResultadoCasoResponse[]
}

export interface SubmissaoResumoResponse {
  id: string
  aluno_id: string
  status: StatusSubmissao
  tempo_execucao_ms: number
  criado_em: string
}

// --- app/schemas/dicas.py -------------------------------------------------
export interface DicaResponse {
  id: string
  problema_id: string
  aluno_id: string
  nivel: number
  conteudo: string
  criado_em: string
}

export interface DicaComEficaciaResponse extends DicaResponse {
  adaptacoes_aplicadas: string[]
  resolvida_apos: boolean
  tempo_ate_resolver_ms: number | null
}

export const NIVEL_DICA_LABEL: Record<number, string> = {
  1: 'Pergunta socrática',
  2: 'Pista conceitual',
  3: 'Pseudocódigo',
  4: 'Solução comentada',
}

// --- app/schemas/error.py -------------------------------------------------
export interface ErrorDetail {
  code: string
  message: string
  fields: Record<string, string[]> | null
}

export interface ErrorResponse {
  error: ErrorDetail
  request_id: string | null
}
