import { render, screen, within } from '@testing-library/react'
import App from './App'

describe('App', () => {
  test('renders hero and generator sections', () => {
    render(<App />)
    // Hero heading: ensure the main tagline is present
    expect(
      screen.getByRole('heading', { name: /Production Code/i })
    ).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Try the Code Generator/i })).toBeInTheDocument()
  })

  test('renders prompt label and theme toggle', () => {
    render(<App />)
    // Scope to the generator section to avoid duplicate 'Prompt' texts elsewhere
    const generatorHeading = screen.getByRole('heading', { name: /Try the Code Generator/i })
    const generatorSection = generatorHeading.closest('section') || document.getElementById('generator') || document.body
    expect(within(generatorSection).getByText(/^Prompt$/i)).toBeInTheDocument()
    // Theme toggle button exists (label changes based on theme)
    const toggle = screen.getByRole('button', { name: /Switch to (dark|light) mode/i })
    expect(toggle).toBeInTheDocument()
  })
})