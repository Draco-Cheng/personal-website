import React from "react";
import styles from "./Footer.module.css";

const Footer: React.FC = () => (
  <footer className={styles.footer} data-testid="footer">
    © 2026 Draco Cheng · Crafted with Next.js & FastAPI
  </footer>
);

export default Footer;