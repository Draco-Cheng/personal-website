"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";

import { usePathname } from "next/navigation";
import styles from "./Menu.module.css";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/ping", label: "Ping API Demo" },
];

const Menu: React.FC = () => {
  const pathname = usePathname();

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
    </nav>
  );
};

export default Menu;