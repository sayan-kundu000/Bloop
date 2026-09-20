import React, { useState } from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  Button,
  Input,
  Textarea,
  Select,
  Modal,
  ConfirmDialog,
  Spinner,
  EmptyState,
} from '../../components/ui';

describe('UI Primitives Foundation', () => {
  describe('Button Component', () => {
    it('renders with children and responds to click events', () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click Me</Button>);

      const button = screen.getByRole('button', { name: /click me/i });
      expect(button).toBeInTheDocument();

      fireEvent.click(button);
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('disables button when disabled or isLoading is true', () => {
      render(
        <Button disabled isLoading>
          Processing
        </Button>
      );

      const button = screen.getByRole('button', { name: /processing/i });
      expect(button).toBeDisabled();
    });

    it('renders different visual variants correctly', () => {
      const { rerender } = render(<Button variant="primary">Primary</Button>);
      expect(screen.getByRole('button')).toHaveClass('bg-indigo-600');

      rerender(<Button variant="danger">Danger</Button>);
      expect(screen.getByRole('button')).toHaveClass('bg-rose-600');

      rerender(<Button variant="secondary">Secondary</Button>);
      expect(screen.getByRole('button')).toHaveClass('bg-slate-800');
    });
  });

  describe('Input Component', () => {
    it('handles value changes and applies error styling when hasError is true', () => {
      const handleChange = vi.fn();
      render(<Input placeholder="Enter prompt" onChange={handleChange} hasError />);

      const input = screen.getByPlaceholderText('Enter prompt');
      expect(input).toHaveClass('border-rose-500');

      fireEvent.change(input, { target: { value: 'New text' } });
      expect(handleChange).toHaveBeenCalled();
    });
  });

  describe('Textarea Component', () => {
    it('renders character count and handles text input', () => {
      render(
        <Textarea
          placeholder="Speech text"
          maxCharacters={100}
          value="Hello World"
          onChange={() => {}}
        />
      );

      expect(screen.getByPlaceholderText('Speech text')).toBeInTheDocument();
      expect(screen.getByText('11 / 100 chars')).toBeInTheDocument();
    });

    it('indicates over-limit styling when text exceeds maxCharacters', () => {
      render(
        <Textarea
          maxCharacters={5}
          value="Longer text than limit"
          onChange={() => {}}
        />
      );

      const counter = screen.getByText(/chars/i);
      expect(counter).toHaveClass('text-rose-400');
    });
  });

  describe('Select Component', () => {
    it('renders dropdown options and responds to selection', () => {
      const handleChange = vi.fn();
      const options = [
        { value: 'en', label: 'English' },
        { value: 'es', label: 'Spanish' },
      ];

      render(<Select options={options} onChange={handleChange} data-testid="select-lang" />);

      const select = screen.getByTestId('select-lang') as HTMLSelectElement;
      expect(select).toBeInTheDocument();
      expect(select.children.length).toBe(2);

      fireEvent.change(select, { target: { value: 'es' } });
      expect(handleChange).toHaveBeenCalled();
    });
  });

  describe('Modal / Dialog Component', () => {
    it('renders modal dialog with accessible attributes when isOpen is true', () => {
      const handleClose = vi.fn();
      render(
        <Modal
          isOpen={true}
          onClose={handleClose}
          title="Voice Settings"
          description="Configure dynamic audio delivery"
        >
          <p>Dialog Body Content</p>
        </Modal>
      );

      const dialog = screen.getByRole('dialog');
      expect(dialog).toHaveAttribute('aria-modal', 'true');
      expect(screen.getByText('Voice Settings')).toBeInTheDocument();
      expect(screen.getByText('Dialog Body Content')).toBeInTheDocument();
    });

    it('does not render when isOpen is false', () => {
      render(
        <Modal isOpen={false} onClose={() => {}}>
          <p>Hidden Content</p>
        </Modal>
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('calls onClose when Escape key is pressed', () => {
      const handleClose = vi.fn();
      render(
        <Modal isOpen={true} onClose={handleClose} title="Test">
          <p>Content</p>
        </Modal>
      );

      fireEvent.keyDown(window, { key: 'Escape', code: 'Escape' });
      expect(handleClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('ConfirmDialog Component', () => {
    it('triggers onConfirm and onClose respectively', () => {
      const handleConfirm = vi.fn();
      const handleClose = vi.fn();

      render(
        <ConfirmDialog
          isOpen={true}
          title="Delete Speech Generation"
          message="Are you sure you want to delete this record?"
          onConfirm={handleConfirm}
          onClose={handleClose}
          isDestructive={true}
          confirmLabel="Delete"
        />
      );

      expect(screen.getByText('Delete Speech Generation')).toBeInTheDocument();
      expect(screen.getByText('Are you sure you want to delete this record?')).toBeInTheDocument();

      const deleteBtn = screen.getByRole('button', { name: /delete/i });
      expect(deleteBtn).toHaveClass('bg-rose-600');
      fireEvent.click(deleteBtn);
      expect(handleConfirm).toHaveBeenCalledTimes(1);

      const cancelBtn = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelBtn);
      expect(handleClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Spinner & EmptyState Components', () => {
    it('renders Spinner with role status and accessible text', () => {
      render(<Spinner label="Generating speech..." />);
      const spinner = screen.getByRole('status');
      expect(spinner).toBeInTheDocument();
      expect(screen.getByText('Generating speech...')).toBeInTheDocument();
    });

    it('renders EmptyState with title, description, and action button', () => {
      render(
        <EmptyState
          title="No speech history yet"
          description="Your generated speech audio will appear here."
          action={<button>Create Speech</button>}
        />
      );

      expect(screen.getByText('No speech history yet')).toBeInTheDocument();
      expect(screen.getByText('Your generated speech audio will appear here.')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create speech/i })).toBeInTheDocument();
    });
  });
});
