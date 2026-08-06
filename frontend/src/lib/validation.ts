import { z } from 'zod'

/** Espelha app/schemas/validators.py:validar_forca_senha - mesma regra
 * checada client-side para feedback imediato; o backend é sempre a fonte
 * de verdade e re-valida de qualquer forma. */
export const senhaSchema = z
  .string()
  .min(8, 'A senha deve ter pelo menos 8 caracteres.')
  .regex(/[A-Za-z]/, 'A senha deve conter pelo menos uma letra.')
  .regex(/\d/, 'A senha deve conter pelo menos um número.')

export const emailSchema = z.string().email('Informe um e-mail válido.')
