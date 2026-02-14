import React from 'react'
import { EmptyStateProps } from '@/lib/types'
import Button from '../ui/Button'

export default function EmptyState({
  message,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 animate-fadeIn">
      <div className="relative mb-6">
        {/* Background circle with pulse effect */}
        <div className="absolute inset-0 bg-primary/10 dark:bg-primary/20 rounded-full blur-2xl animate-pulse" />

        {/* Icon container */}
        <div className="relative bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 p-6 rounded-full animate-scaleIn">
          <svg
            className="w-16 h-16 text-primary dark:text-blue-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
        </div>
      </div>

      <p className="text-lg text-gray-600 dark:text-gray-300 text-center mb-8 max-w-md animate-slideIn">
        {message}
      </p>

      {actionLabel && onAction && (
        <div className="animate-scaleIn">
          <Button variant="primary" onClick={onAction}>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  )
}
