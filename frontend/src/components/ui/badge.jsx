import * as React from "react"

function Badge({ className, variant, children, ...props }) {
  // Simplified badge without class variance authority
  const baseClasses = "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
  
  // Variant classes
  const variantClasses = {
    default: "border-transparent bg-cyan-500 text-white",
    secondary: "border-transparent bg-gray-200 text-gray-900",
    destructive: "border-transparent bg-red-500 text-white",
    outline: "text-gray-300 border-gray-700"
  }
  
  const classes = `${baseClasses} ${variantClasses[variant] || variantClasses.default} ${className || ""}`

  return (
    <div className={classes} {...props}>
      {children}
    </div>
  )
}

export { Badge }