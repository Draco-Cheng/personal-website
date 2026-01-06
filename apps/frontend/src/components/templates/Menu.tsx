"use client";

import React, { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";
import Link from "next/link";
import Image from "next/image";

import { usePathname } from "next/navigation";
import styles from "./Menu.module.css";

const links = [
  // { href: "/", label: "Dashboard" },
];

const Menu: React.FC = () => {
  const pathname = usePathname();
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const stored = window.localStorage.getItem("theme") as "light" | "dark" | null;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initial = stored ?? (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.classList.toggle("dark", initial === "dark");
    document.documentElement.style.colorScheme = initial === "dark" ? "dark" : "light";
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.documentElement.style.colorScheme = theme === "dark" ? "dark" : "light";
    window.localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <nav className={styles.menu}>
      <Link href="/" className={styles.logo}>
        <Image src="/logo-g.png" alt="Logo" fill={true} objectFit="contain" />
      </Link>
      {links.map((link) => (
        <Link
          key={link.href}
          href={link.href}
          className={
            pathname === link.href
              ? `${styles.link} ${styles.active}`
              : styles.link
          }
          aria-current={pathname === link.href ? "page" : undefined}
        >
          {link.label}
        </Link>
      ))}
      <button
        type="button"
        className={styles.themeToggle}
        aria-label="Toggle color theme"
        onClick={toggleTheme}
      >
        {theme === "dark" ? <Moon /> : <Sun />}
      </button>
    </nav>
  );
};

export default Menu;
