import React from "react";
import styles from "./Button.module.css";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  asChild?: boolean;
}

const Button: React.FC<ButtonProps> = ({ children, asChild = false, className, ...props }) => {
  const mergedClassName = [styles.button, className].filter(Boolean).join(" ");

  if (asChild && React.isValidElement(children)) {
    const child = children as React.ReactElement<{ className?: string }>;
    return React.cloneElement(child, {
      className: [mergedClassName, child.props.className].filter(Boolean).join(" "),
      ...props,
    });
  }

  return (
    <button className={mergedClassName} {...props}>
      {children}
    </button>
  );
};

export default Button;
