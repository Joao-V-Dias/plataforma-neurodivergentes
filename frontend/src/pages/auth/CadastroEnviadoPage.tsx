import { Link } from 'react-router-dom'
import { AuthLayout } from './AuthLayout'

export function CadastroEnviadoPage() {
  return (
    <AuthLayout titulo="Cadastro recebido">
      <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-body-sm)' }}>
        Sua conta foi criada e está aguardando aprovação de um professor da sua instituição. Você
        receberá acesso assim que ela for revisada — não é necessário fazer nada agora.
      </p>
      <Link to="/login">Voltar para o login</Link>
    </AuthLayout>
  )
}
