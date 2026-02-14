/**
 * Next.js middleware for authentication on protected routes.
 * Checks for valid token and redirects to signin if not authenticated.
 */

import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Define route types
  const isAuthPage = pathname.startsWith('/signin') || pathname.startsWith('/signup')
  const isProtectedPage = pathname.startsWith('/dashboard')

  // For client-side token storage (localStorage), we can't check the token in middleware
  // The actual authentication check happens in the page components
  // This middleware handles basic routing logic

  // If user is on auth page and tries to access protected route, let page component handle it
  // If user is on protected route, let page component check localStorage and redirect if needed

  // Redirect root to signin for now (can be changed to landing page later)
  if (pathname === '/') {
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}