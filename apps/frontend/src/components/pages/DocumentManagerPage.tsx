"use client";

import React, { useState, useEffect } from "react";
import styles from "./DocumentManagerPage.module.css";
import Footer from "../atoms/Footer";

interface Document {
  id: string;
  filename: string;
  upload_date: string;
  chunk_count: number;
  file_type: string;
}

const ADMIN_KEY_STORAGE = "admin_api_key";
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "/api/admin/documents";

const DocumentManagerPage: React.FC = () => {
  const [apiKey, setApiKey] = useState<string>("");
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [inputKey, setInputKey] = useState<string>("");
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [successMessage, setSuccessMessage] = useState<string>("");

  // Check for stored API key on mount
  useEffect(() => {
    const storedKey = localStorage.getItem(ADMIN_KEY_STORAGE);
    if (storedKey) {
      setApiKey(storedKey);
      verifyAndLoadDocuments(storedKey);
    }
  }, []);

  const verifyAndLoadDocuments = async (key: string) => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${BACKEND_URL}`, {
        headers: {
          "X-API-Key": key,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
        setIsAuthenticated(true);
      } else if (response.status === 401 || response.status === 403) {
        setError("Invalid API key");
        setIsAuthenticated(false);
        localStorage.removeItem(ADMIN_KEY_STORAGE);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Failed to load documents");
      }
    } catch (err) {
      setError("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputKey.trim()) {
      setError("Please enter an API key");
      return;
    }
    localStorage.setItem(ADMIN_KEY_STORAGE, inputKey);
    setApiKey(inputKey);
    verifyAndLoadDocuments(inputKey);
  };

  const handleLogout = () => {
    localStorage.removeItem(ADMIN_KEY_STORAGE);
    setApiKey("");
    setIsAuthenticated(false);
    setDocuments([]);
    setInputKey("");
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError("");
    setSuccessMessage("");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${BACKEND_URL}/upload`, {
        method: "POST",
        headers: {
          "X-API-Key": apiKey,
        },
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setSuccessMessage(`${file.name} uploaded successfully! (${data.chunk_count} chunks)`);
        // Reload documents
        await verifyAndLoadDocuments(apiKey);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Upload failed");
      }
    } catch (err) {
      setError("Failed to upload file");
    } finally {
      setUploading(false);
      // Reset file input
      e.target.value = "";
    }
  };

  const handleDelete = async (documentId: string, filename: string) => {
    if (!confirm(`Are you sure you want to delete "${filename}"? This action cannot be undone.`)) {
      return;
    }

    setError("");
    setSuccessMessage("");

    try {
      const response = await fetch(`${BACKEND_URL}/${documentId}`, {
        method: "DELETE",
        headers: {
          "X-API-Key": apiKey,
        },
      });

      if (response.ok) {
        setSuccessMessage(`${filename} deleted successfully`);
        // Reload documents
        await verifyAndLoadDocuments(apiKey);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Delete failed");
      }
    } catch (err) {
      setError("Failed to delete document");
    }
  };

  // Login screen
  if (!isAuthenticated) {
    return (
      <div className={styles.page}>
        <div className={styles.loginContainer}>
          <h1 className={styles.title}>Document Manager</h1>
          <p className={styles.subtitle}>Enter your admin API key to continue</p>
          <form onSubmit={handleLogin} className={styles.loginForm}>
            <input
              type="password"
              placeholder="Admin API Key"
              value={inputKey}
              onChange={(e) => setInputKey(e.target.value)}
              className={styles.input}
              autoFocus
            />
            <button type="submit" className={styles.loginButton} disabled={loading}>
              {loading ? "Verifying..." : "Login"}
            </button>
          </form>
          {error && <p className={styles.error}>{error}</p>}
        </div>
        <Footer />
      </div>
    );
  }

  // Document management screen
  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>Document Manager</h1>
          <button onClick={handleLogout} className={styles.logoutButton}>
            Logout
          </button>
        </div>
        <div className={styles.uploadSection}>
          <label className={styles.uploadButton}>
            {uploading ? "Uploading..." : "Upload Document"}
            <input
              type="file"
              onChange={handleFileUpload}
              accept=".pdf,.docx,.xlsx,.md,.markdown,.txt"
              disabled={uploading}
              className={styles.fileInput}
            />
          </label>
          <p className={styles.uploadHint}>
            Supported: PDF, Word (.docx), Excel (.xlsx), Markdown (.md), Text (.txt)
          </p>
        </div>
      </header>

      {error && <div className={styles.errorBanner}>{error}</div>}
      {successMessage && <div className={styles.successBanner}>{successMessage}</div>}

      <section className={styles.documentsSection}>
        {loading ? (
          <p className={styles.loading}>Loading documents...</p>
        ) : documents.length === 0 ? (
          <div className={styles.emptyState}>
            <p className={styles.emptyTitle}>No documents uploaded yet</p>
            <p className={styles.emptySubtitle}>
              Upload a document to get started with RAG-powered chat
            </p>
          </div>
        ) : (
          <div className={styles.documentList}>
            {documents.map((doc) => (
              <div key={doc.id} className={styles.documentCard}>
                <div className={styles.documentIcon}>
                  {getFileIcon(doc.file_type)}
                </div>
                <div className={styles.documentInfo}>
                  <h3 className={styles.documentName}>{doc.filename}</h3>
                  <p className={styles.documentMeta}>
                    {new Date(doc.upload_date).toLocaleDateString()} · {doc.chunk_count} chunks
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(doc.id, doc.filename)}
                  className={styles.deleteButton}
                  title={`Delete ${doc.filename}`}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        )}
      </section>

      <Footer />
    </div>
  );
};

function getFileIcon(fileType: string): string {
  const iconMap: Record<string, string> = {
    pdf: "📄",
    docx: "📝",
    doc: "📝",
    xlsx: "📊",
    xls: "📊",
    md: "📃",
    markdown: "📃",
    txt: "📃",
  };
  return iconMap[fileType.toLowerCase()] || "📄";
}

export default DocumentManagerPage;
