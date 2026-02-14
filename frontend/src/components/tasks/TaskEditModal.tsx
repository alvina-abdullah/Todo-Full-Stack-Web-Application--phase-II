'use client'

import React from 'react'
import { Task } from '@/lib/types'
import Modal from '../ui/Modal'
import TaskForm from './TaskForm'

interface TaskEditModalProps {
  task: Task | null
  isOpen: boolean
  onClose: () => void
  onSave: (taskId: number, data: { title: string; description: string }) => Promise<void>
}

export default function TaskEditModal({
  task,
  isOpen,
  onClose,
  onSave,
}: TaskEditModalProps) {
  if (!task) return null

  const handleSubmit = async (data: { title: string; description: string }) => {
    await onSave(task.id, data)
    onClose()
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
            <svg className="w-4 h-4 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <span>Edit Task</span>
        </div>
      }
      size="md"
    >
      <TaskForm
        initialValues={{
          title: task.title,
          description: task.description || '',
        }}
        onSubmit={handleSubmit}
        onCancel={onClose}
        submitLabel="Save Changes"
      />
    </Modal>
  )
}
