import * as React from "react"

const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  // Simplified button without class variance authority
  const baseClasses = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background"
  
  // Variant classes
  const variantClasses = {
    default: "bg-cyan-500 text-white hover:bg-cyan-600",
    destructive: "bg-red-500 text-white hover:bg-red-600",
    outline: "border border-gray-300 hover:bg-gray-100",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    ghost: "hover:bg-gray-100",
    link: "underline-offset-4 hover:underline text-cyan-500"
  }
  
  // Size classes
  const sizeClasses = {
    default: "h-10 py-2 px-4",
    sm: "h-9 px-3 rounded-md",
    lg: "h-11 px-8 rounded-md",
    icon: "h-10 w-10"
  }
  
  const classes = `${baseClasses} ${variantClasses[variant] || variantClasses.default} ${sizeClasses[size] || sizeClasses.default} ${className || ""}`

  const Comp = asChild ? React.Fragment : "button"
  return (
    <Comp
      className={classes}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }