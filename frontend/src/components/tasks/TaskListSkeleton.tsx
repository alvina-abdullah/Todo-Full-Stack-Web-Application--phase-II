import React from 'react'

export default function TaskListSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 shadow-md animate-fadeIn"
          style={{ animationDelay: `${i * 50}ms` }}
        >
          <div className="flex items-start gap-4">
            {/* Checkbox skeleton */}
            <div className="flex-shrink-0 pt-1">
              <div className="w-6 h-6 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
            </div>

            <div className="flex-1 space-y-3">
              {/* Title skeleton */}
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-lg w-3/4 animate-shimmer"></div>

              {/* Description skeleton */}
              <div className="space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-lg w-full animate-shimmer"></div>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-lg w-5/6 animate-shimmer"></div>
              </div>

              {/* Metadata skeleton */}
              <div className="flex items-center gap-4">
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-32 animate-shimmer"></div>
              </div>
            </div>

            {/* Action buttons skeleton */}
            <div className="flex flex-col gap-2">
              <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
              <div className="w-20 h-8 bg-gray-200 dark:bg-gray-700 rounded-lg animate-shimmer"></div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
