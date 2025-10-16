import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  test('renders hero and generator sections', () => {
    render(<App />)
    expect(screen.getByText(/Natural Language/i)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Try the Code Generator/i })).toBeInTheDocument()
  })

  test('renders prompt label and theme toggle', () => {
    render(<App />)
    // Prompt label
    expect(screen.getByText(/Prompt/i)).toBeInTheDocument()
    // Theme toggle button exists (label changes based on theme)
    const toggle = screen.getByRole('button', { name: /Switch to (dark|light) mode/i })
    expect(toggle).toBeInTheDocument()
  })
})