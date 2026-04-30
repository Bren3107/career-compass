export function StepIndicator({ currentStep }) {
  return (
    <div className="step-indicator">
      {[1, 2, 3].map((step) => (
        <div
          key={step}
          className={`step-dot ${step === currentStep ? 'active' : ''} ${step < currentStep ? 'active' : ''}`}
        />
      ))}
    </div>
  )
}
