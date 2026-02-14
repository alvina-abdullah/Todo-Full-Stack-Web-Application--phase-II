'use client'

import React, { useState } from 'react'
import { TaskFormProps } from '@/lib/types'
import Input from '../ui/Input'
import Textarea from '../ui/Textarea'
import Button from '../ui/Button'

export default function TaskForm({
  initialValues,
  onSubmit,
  onCancel,
  submitLabel = 'Create Task',
  cancelLabel = 'Cancel',
}: TaskFormProps) {
  const [formState, setFormState] = useState({
    title: initialValues?.title || '',
    description: initialValues?.description || '',
    errors: {} as { title?: string; description?: string },
    submitting: false,
    touched: { title: false, description: false },
  })

  const validateTitle = (value: string) => {
    if (!value.trim()) {
      return 'Title is required'
    }
    if (value.length > 200) {
      return 'Title must be 200 characters or less'
    }
    return ''
  }

  const validateDescription = (value: string) => {
    if (value.length > 2000) {
      return 'Description must be 2000 characters or less'
    }
    return ''
  }

  const handleTitleBlur = () => {
    const error = validateTitle(formState.title)
    setFormState(prev => ({
      ...prev,
      touched: { ...prev.touched, title: true },
      errors: { ...prev.errors, title: error },
    }))
  }

  const handleDescriptionBlur = () => {
    const error = validateDescription(formState.description)
    setFormState(prev => ({
      ...prev,
      touched: { ...prev.touched, description: true },
      errors: { ...prev.errors, description: error },
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Validate all fields
    const titleError = validateTitle(formState.title)
    const descriptionError = validateDescription(formState.description)

    if (titleError || descriptionError) {
      setFormState(prev => ({
        ...prev,
        errors: { title: titleError, description: descriptionError },
        touched: { title: true, description: true },
      }))
      return
    }

    setFormState(prev => ({ ...prev, submitting: true }))

    try {
      await onSubmit({
        title: formState.title,
        description: formState.description,
      })
      // Success - parent will handle closing form
    } catch (error) {
      setFormState(prev => ({
        ...prev,
        submitting: false,
        errors: { title: error instanceof Error ? error.message : 'Failed to save task' },
      }))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 animate-fadeIn">
      <Input
        id="title"
        name="title"
        label="Task Title"
        value={formState.title}
        onChange={(value) => setFormState(prev => ({ ...prev, title: value }))}
        onBlur={handleTitleBlur}
        error={formState.touched.title ? formState.errors.title : undefined}
        required
        maxLength={200}
        placeholder="Enter task title"
        disabled={formState.submitting}
      />

      <Textarea
        id="description"
        name="description"
        label="Description"
        value={formState.description}
        onChange={(value) => setFormState(prev => ({ ...prev, description: value }))}
        onBlur={handleDescriptionBlur}
        error={formState.touched.description ? formState.errors.description : undefined}
        maxLength={2000}
        rows={4}
        placeholder="Enter task description (optional)"
        disabled={formState.submitting}
      />

      <div className="flex gap-3 justify-end pt-4 border-t border-gray-200 dark:border-gray-700">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={formState.submitting}
        >
          {cancelLabel}
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={formState.submitting}
          disabled={formState.submitting}
        >
          {submitLabel}
        </Button>
      </div>
    </form>
  )
}
