import React from "react";
import Link from "next/link";
import Button from "../atoms/Button";
import Footer from "../atoms/Footer";
import styles from "./ProfilePage.module.css";

const highlights = [
  { label: "Years shipping products", value: "12+" },
  { label: "Projects launched", value: "12" },
  { label: "Mentored engineers", value: "5" },
];

const experience = [
  {
    role: "Senior Software Developer",
    company: "Trend Micro",
    period: "2019 — 2025",
    summary:
      "Scaled a cross-region monorepo platform spanning React, Node, and Pulumi; drove AI-assisted delivery, mentored four engineers, and embedded Nx + Cypress patterns into large Angular initiatives.",
  },
  {
    role: "Senior Software Developer",
    company: "London Stock Exchange Group (Yield Book)",
    period: "2018 — 2019",
    summary:
      "Led frontend work for fixed-income analytics, automated reporting with BIRT, and shipped internal tooling that surfaced critical server telemetry for ops teams.",
  },
  {
    role: "Senior Software Developer",
    company: "Isentia",
    period: "2017",
    summary:
      "Rebuilt internal admin and demo apps with refreshed UX patterns, adding rapid customization paths for enterprise media clients.",
  },
  {
    role: "Software Developer",
    company: "Elastic Grid",
    period: "2016 — 2017",
    summary:
      "Delivered multilingual campaign microsites and EDM systems for NetApp, Juniper, Atlassian, and Veritas with responsive design upgrades.",
  },
  {
    role: "Software Developer",
    company: "Ubitus",
    period: "2012 — 2016",
    summary:
      "Built secure middleware plus Ember.js web apps powering cloud gaming across Xbox One, Samsung, and major telecom ecosystems.",
  },
];

const projects = [
  {
    name: "Mono Repo Skeleton",
    description:
      "Nx-powered template that ships a Next.js 15 frontend and FastAPI backend with Docker, Helm charts, and CI-ready testing presets.",
    link: "https://github.com/Draco-Cheng/mono-repo-skeleton",
  },
  {
    name: "AI_README MCP Server",
    description:
      "Model Context Protocol server that discovers, routes, and validates AI_README guides so coding copilots follow team conventions by default.",
    link: "https://github.com/Draco-Cheng/ai-readme-mcp",
  },
];

const socials = [
  { label: "GitHub", href: "https://github.com/Draco-Cheng" },
  { label: "LinkedIn", href: "https://www.linkedin.com/in/draco-cheng/" },
];

const contactLinks = [
  { label: "Email", href: "mailto:draco.cheng@outlook.com" }
];

const ProfilePage: React.FC = () => (
  <div className={styles.page}>
    <section className={styles.hero}>
      <p className={styles.eyebrow}>Full-stack Engineer · Product Architect</p>
      <h1 className={styles.title}>Hi, I’m Draco Cheng.</h1>
      <p className={styles.subtitle}>
        I craft resilient, accessible web apps with a focus on delightful developer experience and measurable outcomes.
      </p>
      <div className={styles.actions}>
        <Button asChild>
          <Link href="/resume.pdf" target="_blank" rel="noopener noreferrer">
            Download Résumé
          </Link>
        </Button>
        <Link className={styles.secondaryAction} href="#projects">
          View projects
        </Link>
      </div>
      <div className={styles.socials}>
        {socials.map((social) => (
          <Link key={social.label} href={social.href} target="_blank" rel="noopener noreferrer">
            {social.label}
          </Link>
        ))}
      </div>
    </section>

    <section className={styles.highlightGrid}>
      {highlights.map((highlight) => (
        <article key={highlight.label} className={styles.highlightCard}>
          <span className={styles.highlightValue}>{highlight.value}</span>
          <span className={styles.highlightLabel}>{highlight.label}</span>
        </article>
      ))}
    </section>

    <section className={styles.split}>
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>Experience</p>
          <h2 className={styles.sectionTitle}>Building thoughtful teams & tools</h2>
        </div>
        <ol className={styles.timeline}>
          {experience.map((entry) => (
            <li key={entry.role} className={styles.timelineItem}>
              <div>
                <p className={styles.timelineRole}>{entry.role}</p>
                <p className={styles.timelineCompany}>{entry.company}</p>
              </div>
              <p className={styles.timelinePeriod}>{entry.period}</p>
              <p className={styles.timelineSummary}>{entry.summary}</p>
            </li>
          ))}
        </ol>
      </div>

      <div id="projects" className={styles.section}>
        <div className={styles.sectionHeader}>
          <p className={styles.sectionEyebrow}>Selected Work</p>
          <h2 className={styles.sectionTitle}>Product case studies</h2>
        </div>
        <div className={styles.projectList}>
          {projects.map((project) => (
            <article key={project.name} className={styles.projectCard}>
              <div>
                <h3 className={styles.projectName}>{project.name}</h3>
                <p className={styles.projectDescription}>{project.description}</p>
              </div>
              <Link
                href={project.link}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.projectLink}
              >
                Read more →
              </Link>
            </article>
          ))}
        </div>
      </div>
    </section>

    <section className={styles.contact}>
      <p className={styles.sectionEyebrow}>Let’s collaborate</p>
      <h2 className={styles.contactTitle}>Have an idea in mind?</h2>
      <p className={styles.contactSubtitle}>
        I’m currently open to senior engineering roles, advisory work, and short-term product sprints.
      </p>
      <div className={styles.contactActions}>
        {contactLinks.map((link) => (
          <Link key={link.label} href={link.href} target="_blank" rel="noopener noreferrer">
            {link.label}
          </Link>
        ))}
      </div>
    </section>

    <Footer />
  </div>
);

export default ProfilePage;
