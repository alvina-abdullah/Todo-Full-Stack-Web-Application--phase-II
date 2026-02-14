import React from 'react'
import { TaskListProps } from '@/lib/types'
import TaskItem from './TaskItem'
import TaskListSkeleton from './TaskListSkeleton'
import ErrorMessage from '../ui/ErrorMessage'
import EmptyState from './EmptyState'

export default function TaskList({
  tasks,
  loading,
  error,
  onToggleComplete,
  onEdit,
  onDelete,
  onRetry,
}: TaskListProps) {
  if (loading) {
    return <TaskListSkeleton />
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={onRetry}
        onDismiss={onRetry}
      />
    )
  }

  if (tasks.length === 0) {
    return (
      <EmptyState
        message="No tasks yet. Create your first task to get started!"
        actionLabel="Create Task"
        onAction={() => {
          // This will be handled by parent component
          const createButton = document.querySelector('[data-create-task]') as HTMLButtonElement
          createButton?.click()
        }}
      />
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onToggleComplete={onToggleComplete}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  )
}
