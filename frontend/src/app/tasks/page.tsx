'use client'

import { useState, useEffect } from 'react'
import { Task } from '@/lib/types'
import { signOut } from '@/lib/auth-utils'
import { apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api-client'
import Header from '@/components/layout/Header'
import TaskList from '@/components/tasks/TaskList'
import TaskForm from '@/components/tasks/TaskForm'
import TaskEditModal from '@/components/tasks/TaskEditModal'
import DeleteConfirmDialog from '@/components/tasks/DeleteConfirmDialog'
import Button from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | null>(null)
  const [deletingTask, setDeletingTask] = useState<Task | null>(null)
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all')

  // Fetch tasks on mount
  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiGet('/api/v1/tasks')

      if (!response.ok) {
        throw new Error('Failed to load tasks')
      }

      const data = await response.json()
      setTasks(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks. Please try again.')
      console.error('Load tasks error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateTask = async (data: { title: string; description: string }) => {
    try {
      const response = await apiPost('/api/v1/tasks', {
        title: data.title,
        description: data.description || null,
      })

      if (!response.ok) {
        throw new Error('Failed to create task')
      }

      // Refetch tasks to ensure consistency
      await fetchTasks()
      setShowCreateForm(false)
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create task')
    }
  }

  const handleUpdateTask = async (taskId: number, data: { title: string; description: string }) => {
    try {
      const response = await apiPatch(`/api/v1/tasks/${taskId}`, {
        title: data.title,
        description: data.description || null,
      })

      if (!response.ok) {
        throw new Error('Failed to update task')
      }

      // Refetch tasks to ensure consistency
      await fetchTasks()
      setEditingTask(null)
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to update task')
    }
  }

  const handleDeleteTask = async (taskId: number) => {
    try {
      const response = await apiDelete(`/api/v1/tasks/${taskId}`)

      if (!response.ok) {
        throw new Error('Failed to delete task')
      }

      // Refetch tasks to ensure consistency
      await fetchTasks()
      setDeletingTask(null)
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to delete task')
    }
  }

  const handleToggleComplete = async (task: Task) => {
    // Optimistic update
    setTasks(tasks.map(t =>
      t.id === task.id ? { ...t, completed: !t.completed } : t
    ))

    try {
      const response = await apiPatch(`/api/v1/tasks/${task.id}`, {
        completed: !task.completed,
      })

      if (!response.ok) {
        throw new Error('Failed to update task')
      }

      // Refetch to confirm state
      await fetchTasks()
    } catch (err) {
      // Rollback via refetch
      setError('Failed to update task')
      await fetchTasks()
    }
  }

  const handleSignOut = async () => {
    await signOut()
  }

  // Filter tasks based on selected filter
  const filteredTasks = tasks.filter(task => {
    if (filter === 'active') return !task.completed
    if (filter === 'completed') return task.completed
    return true
  })

  // Calculate stats
  const totalTasks = tasks.length
  const completedTasks = tasks.filter(t => t.completed).length
  const activeTasks = totalTasks - completedTasks
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Header title="My Tasks" onSignOut={handleSignOut} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total Tasks</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{totalTasks}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Active</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{activeTasks}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Completed</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{completedTasks}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Progress</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{completionRate}%</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Actions Bar */}
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-lg border border-gray-200 dark:border-gray-700 mb-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            {/* Filter Tabs */}
            <div className="flex gap-2 bg-gray-50 dark:bg-gray-900/50 p-1 rounded-xl">
              <button
                onClick={() => setFilter('all')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  filter === 'all'
                    ? 'bg-primary text-white shadow-lg shadow-blue-500/30 scale-105'
                    : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105'
                }`}
              >
                All ({totalTasks})
              </button>
              <button
                onClick={() => setFilter('active')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  filter === 'active'
                    ? 'bg-primary text-white shadow-lg shadow-blue-500/30 scale-105'
                    : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105'
                }`}
              >
                Active ({activeTasks})
              </button>
              <button
                onClick={() => setFilter('completed')}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
                  filter === 'completed'
                    ? 'bg-primary text-white shadow-lg shadow-blue-500/30 scale-105'
                    : 'bg-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:scale-105'
                }`}
              >
                Completed ({completedTasks})
              </button>
            </div>

            {/* Create Button */}
            <Button
              variant="primary"
              onClick={() => setShowCreateForm(true)}
              data-create-task
              className="shadow-lg shadow-blue-500/30"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Create Task
            </Button>
          </div>
        </div>

        {/* Task List */}
        <TaskList
          tasks={filteredTasks}
          loading={loading}
          error={error}
          onToggleComplete={handleToggleComplete}
          onEdit={setEditingTask}
          onDelete={setDeletingTask}
          onRetry={fetchTasks}
        />
      </div>

      {/* Create Task Modal */}
      <Modal
        isOpen={showCreateForm}
        onClose={() => setShowCreateForm(false)}
        title="Create New Task"
        size="md"
      >
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setShowCreateForm(false)}
          submitLabel="Create Task"
        />
      </Modal>

      {/* Edit Task Modal */}
      <TaskEditModal
        task={editingTask}
        isOpen={!!editingTask}
        onClose={() => setEditingTask(null)}
        onSave={handleUpdateTask}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmDialog
        task={deletingTask}
        isOpen={!!deletingTask}
        onClose={() => setDeletingTask(null)}
        onConfirm={handleDeleteTask}
      />
    </div>
  )
}
