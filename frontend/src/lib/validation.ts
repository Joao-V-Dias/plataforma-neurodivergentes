import { z } from 'zod'

export const senhaSchema = z
  .string()
  .min(8, 'A senha precisa de ao menos 8 caracteres.')
  .max(128, 'A senha pode ter no máximo 128 caracteres.')
  .refine((v) => /[a-z]/.test(v), 'Inclua ao menos uma letra minúscula.')
  .refine((v) => /[A-Z]/.test(v), 'Inclua ao menos uma letra maiúscula.')
  .refine((v) => /[0-9]/.test(v), 'Inclua ao menos um número.')

export const emailSchema = z.string().min(1, 'Informe seu e-mail.').email('E-mail inválido.')
