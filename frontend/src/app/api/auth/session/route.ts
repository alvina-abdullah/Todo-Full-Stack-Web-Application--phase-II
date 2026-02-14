/**
 * Better Auth API route handler.
 *
 * This catch-all route handles all Better Auth API requests:
 * - POST /api/auth/sign-up - User registration
 * - POST /api/auth/sign-in - User sign in
 * - POST /api/auth/sign-out - User sign out
 * - GET /api/auth/session - Get current session
 * - And other Better Auth endpoints
 */

import { auth } from "@/lib/auth";
import { NextResponse } from 'next/server'

export async function GET(req: Request) {
  try {
    const session = await auth.api.getSession({
      headers: req.headers,
    })

    return NextResponse.json({ session })
  } catch {
    return NextResponse.json({ session: null }, { status: 401 })
  }
}
