import { NextRequest, NextResponse } from 'next/server'
import { getApiSession } from '@/lib/api-auth'
import { getUserSubscription, upgradeUserSubscription } from '@/lib/user-learning-store'

export async function GET() {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  const sub = getUserSubscription(user.id, user.email)
  return NextResponse.json({
    status: 'success',
    subscription: sub,
    isPro: sub.tier === 'pro'
  })
}

export async function POST(req: NextRequest) {
  const { user, errorResponse } = await getApiSession()
  if (errorResponse) return errorResponse

  try {
    const body = await req.json()
    const tier = body.tier === 'pro' ? 'pro' : 'free'
    const updated = upgradeUserSubscription(user.id, user.email, tier)

    return NextResponse.json({
      status: 'success',
      subscription: updated,
      message: tier === 'pro' 
        ? 'Congratulations! StudySync Pro Scholar plan activated. Unlimited AI tutoring, paper solving, and advanced models unlocked.' 
        : 'Switched to StudySync Student Free plan.'
    })
  } catch (error: any) {
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 })
  }
}
