import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { AuthView } from '@/components/auth-view'
import { auth } from '@/lib/auth'

export default async function AuthPage() {
  const session = await auth.api.getSession({ headers: await headers() })
  if (session?.user) redirect('/')
  return <AuthView />
}
