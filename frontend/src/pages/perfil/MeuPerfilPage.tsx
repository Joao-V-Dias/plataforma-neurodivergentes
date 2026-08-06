import { useAuth } from '@/lib/auth/useAuth'
import { PAPEL_LABEL } from '@/lib/api/types'
import { Card, CardHeader } from '@/components/ui/Card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs'
import { NeurodivergenciaSection } from './NeurodivergenciaSection'
import { BigFiveSection } from './BigFiveSection'

export function MeuPerfilPage() {
  const { usuario } = useAuth()
  if (!usuario) return null

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader title="Minha conta" />
        <dl className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <dt className="text-[var(--color-muted)]">Nome</dt>
            <dd className="font-medium text-[var(--color-fg)]">{usuario.nome}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">E-mail</dt>
            <dd className="font-medium text-[var(--color-fg)]">{usuario.email}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Papel</dt>
            <dd className="font-medium text-[var(--color-fg)]">{PAPEL_LABEL[usuario.papel]}</dd>
          </div>
          <div>
            <dt className="text-[var(--color-muted)]">Conta desde</dt>
            <dd className="font-medium text-[var(--color-fg)]">
              {new Date(usuario.created_at).toLocaleDateString('pt-BR')}
            </dd>
          </div>
        </dl>
      </Card>

      {usuario.papel === 'aluno' && (
        <Tabs defaultValue="neurodivergencia">
          <TabsList aria-label="Seções do perfil de adaptação">
            <TabsTrigger value="neurodivergencia">Neurodivergência</TabsTrigger>
            <TabsTrigger value="big-five">Perfil Big Five</TabsTrigger>
          </TabsList>
          <TabsContent value="neurodivergencia">
            <NeurodivergenciaSection />
          </TabsContent>
          <TabsContent value="big-five">
            <BigFiveSection />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
