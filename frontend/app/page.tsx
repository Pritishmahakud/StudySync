import { headers } from 'next/headers'
import { redirect } from 'next/navigation'
import { StudySync } from '@/components/study-sync'
import { auth } from '@/lib/auth'

export default async function Home() {
  const session = await auth.api.getSession({ headers: await headers() })
  if (!session?.user) redirect('/auth')
  return <StudySync user={{ name: session.user.name, email: session.user.email, major: session.user.major, image: session.user.image, createdAt: session.user.createdAt }} />
}
