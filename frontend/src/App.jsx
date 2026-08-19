import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "https://codeforge-ai-production-b2d0.up.railway.app";

function getRepositoryName(url) {
  try {
    const cleanUrl = url.trim().replace(/\/+$/, "");

    if (!cleanUrl) {
      return "";
    }

    let name = cleanUrl.split("/").pop();

    if (name.endsWith(".git")) {
      name = name.slice(0, -4);
    }

    return name;
  } catch {
    return "";
  }
}

function App() {
  // --------------------------------------------------
  // Repository state
  // --------------------------------------------------

  const [repoUrl, setRepoUrl] = useState(() => {
    return localStorage.getItem("codeforge_repo_url") || "";
  });

  const [repository, setRepository] = useState(() => {
    try {
      const savedRepository =
        localStorage.getItem("codeforge_repository");

      return savedRepository
        ? JSON.parse(savedRepository)
        : null;
    } catch {
      return null;
    }
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // File viewer state
  // --------------------------------------------------

  const [selectedFile, setSelectedFile] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState("");

  // --------------------------------------------------
  // Ask AI state
  // --------------------------------------------------

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [asking, setAsking] = useState(false);
  const [questionError, setQuestionError] = useState("");

  // --------------------------------------------------
  // Persist repository URL
  // --------------------------------------------------

  useEffect(() => {
    if (repoUrl.trim()) {
      localStorage.setItem(
        "codeforge_repo_url",
        repoUrl
      );
    }
  }, [repoUrl]);

  // --------------------------------------------------
  // Persist repository analysis
  // --------------------------------------------------

  useEffect(() => {
    if (repository) {
      localStorage.setItem(
        "codeforge_repository",
        JSON.stringify(repository)
      );
    }
  }, [repository]);

  // --------------------------------------------------
  // Analyze repository
  // --------------------------------------------------

  const analyzeRepository = async () => {
    if (!repoUrl.trim()) {
      setError(
        "Please enter a GitHub repository URL."
      );
      return;
    }

    setLoading(true);
    setError("");

    setRepository(null);
    setSelectedFile("");
    setFileContent("");
    setFileError("");

    setAnswer("");
    setSources([]);
    setQuestionError("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/repositories/analyze?repo_url=${encodeURIComponent(
          repoUrl.trim()
        )}`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to analyze repository."
        );
      }

      setRepository(data);

      // Save immediately instead of waiting for useEffect.
      localStorage.setItem(
        "codeforge_repository",
        JSON.stringify(data)
      );

      localStorage.setItem(
        "codeforge_repo_url",
        repoUrl.trim()
      );

    } catch (error) {
      console.error(
        "Repository analysis error:",
        error
      );

      setError(
        error.message ||
          "Failed to analyze repository."
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // Handle Enter in repository input
  // --------------------------------------------------

  const handleRepositoryKeyDown = (event) => {
    if (event.key === "Enter") {
      analyzeRepository();
    }
  };

  // --------------------------------------------------
  // Open repository file
  // --------------------------------------------------

  const openFile = async (filePath) => {
    if (!repository) {
      return;
    }

    setSelectedFile(filePath);
    setFileContent("");
    setFileError("");
    setFileLoading(true);

    try {
      const normalizedPath =
        filePath.replace(/\\/g, "/");

      const response = await fetch(
        `${API_BASE_URL}/api/repositories/file?repository=${encodeURIComponent(
          repository.repository
        )}&file_path=${encodeURIComponent(
          normalizedPath
        )}`,
        {
          method: "GET",
          headers: {
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to load file."
        );
      }

      setFileContent(
        data.content || ""
      );

    } catch (error) {
      console.error(
        "File loading error:",
        error
      );

      setFileError(
        error.message ||
          "Failed to load file."
      );
    } finally {
      setFileLoading(false);
    }
  };

  // --------------------------------------------------
  // Ask CodeForge AI
  // --------------------------------------------------

  const askQuestion = async () => {
    if (!question.trim()) {
      setQuestionError(
        "Please enter a question."
      );
      return;
    }

    const repositoryName =
      repository?.repository ||
      getRepositoryName(repoUrl);

    if (!repositoryName) {
      setQuestionError(
        "Please enter a GitHub repository URL first."
      );
      return;
    }

    setAsking(true);
    setQuestionError("");
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/questions/ask?question=${encodeURIComponent(
          question.trim()
        )}&repository=${encodeURIComponent(
          repositoryName
        )}`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
            "Failed to get AI answer."
        );
      }

      setAnswer(
        data.answer ||
          "No answer was generated."
      );

      setSources(
        Array.isArray(data.sources)
          ? data.sources
          : []
      );

    } catch (error) {
      console.error(
        "Ask AI error:",
        error
      );

      setQuestionError(
        error.message ||
          "Failed to get AI answer."
      );
    } finally {
      setAsking(false);
    }
  };

  // --------------------------------------------------
  // Handle Enter in Ask AI input
  // --------------------------------------------------

  const handleQuestionKeyDown = (event) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      askQuestion();
    }
  };

  // --------------------------------------------------
  // Clear saved repository
  // --------------------------------------------------

  const clearRepository = () => {
    localStorage.removeItem(
      "codeforge_repo_url"
    );

    localStorage.removeItem(
      "codeforge_repository"
    );

    setRepoUrl("");
    setRepository(null);

    setSelectedFile("");
    setFileContent("");
    setFileError("");

    setQuestion("");
    setAnswer("");
    setSources([]);
    setQuestionError("");
    setError("");
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------

  return (
    <div className="app">

      {/* -------------------------------------------- */}
      {/* Navbar */}
      {/* -------------------------------------------- */}

      <header className="navbar">

        <div className="logo">
          CodeForge AI
        </div>

        <div className="nav-status">
          <span className="status-dot"></span>
          AI Code Intelligence
        </div>

      </header>

      {/* -------------------------------------------- */}
      {/* Main */}
      {/* -------------------------------------------- */}

      <main className="container">

        {/* ------------------------------------------ */}
        {/* Hero */}
        {/* ------------------------------------------ */}

        <section className="hero">

          <h1>
            Understand any codebase with AI.
          </h1>

          <p>
            Connect a public GitHub repository
            and explore its codebase using
            AI-powered semantic search and RAG.
          </p>

          <div className="repo-input">

            <input
              type="text"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(event) =>
                setRepoUrl(event.target.value)
              }
              onKeyDown={
                handleRepositoryKeyDown
              }
            />

            <button
              onClick={analyzeRepository}
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Analyze Repository"}
            </button>

          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {repository && (
            <div className="repository-status">

              <span className="success-icon">
                ✓
              </span>

              <span>
                Repository analyzed
              </span>

              <button
                className="clear-repository"
                onClick={clearRepository}
              >
                Clear
              </button>

            </div>
          )}

        </section>

        {/* ------------------------------------------ */}
        {/* Repository Dashboard */}
        {/* ------------------------------------------ */}

        {repository && (

          <section className="dashboard">

            <div className="repository-header">

              <div>

                <span className="label">
                  Repository
                </span>

                <h2>
                  {repository.repository}
                </h2>

              </div>

            </div>

            {/* -------------------------------------- */}
            {/* Statistics */}
            {/* -------------------------------------- */}

            <div className="stats">

              <div className="stat-card">

                <span>
                  Total Files
                </span>

                <strong>
                  {repository.total_files}
                </strong>

              </div>

              <div className="stat-card">

                <span>
                  Source Files
                </span>

                <strong>
                  {repository.source_files}
                </strong>

              </div>

            </div>

            {/* -------------------------------------- */}
            {/* Files + Code Viewer */}
            {/* -------------------------------------- */}

            <div className="code-explorer">

              {/* File list */}

              <div className="files-section">

                <h3>
                  Repository Files
                </h3>

                <div className="file-list">

                  {repository.files.map(
                    (file, index) => (

                      <button
                        className={`file-item ${
                          selectedFile === file
                            ? "selected"
                            : ""
                        }`}
                        key={`${file}-${index}`}
                        onClick={() =>
                          openFile(file)
                        }
                      >

                        <span>
                          📄
                        </span>

                        <span>
                          {file}
                        </span>

                      </button>

                    )
                  )}

                </div>

              </div>

              {/* Code viewer */}

              <div className="code-viewer">

                <h3>
                  Code Viewer
                </h3>

                {!selectedFile && (
                  <div className="empty-viewer">
                    Select a file to view
                    its source code.
                  </div>
                )}

                {selectedFile && (
                  <>
                    <div className="selected-file">
                      📄 {selectedFile}
                    </div>

                    {fileLoading && (
                      <div className="empty-viewer">
                        Loading file...
                      </div>
                    )}

                    {fileError && (
                      <div className="error">
                        {fileError}
                      </div>
                    )}

                    {!fileLoading &&
                      !fileError && (
                        <pre className="code-content">
                          <code>
                            {fileContent}
                          </code>
                        </pre>
                      )}

                  </>
                )}

              </div>

            </div>

          </section>
        )}

        {/* ------------------------------------------ */}
        {/* Ask AI */}
        {/* ------------------------------------------ */}

        <section className="ask-section">

          <div className="ask-header">

            <span className="label">
              AI CODE ASSISTANT
            </span>

            <h2>
              Ask CodeForge AI
            </h2>

            <p>
              Ask questions about this
              repository. CodeForge AI will
              search the codebase and generate
              an answer using RAG.
            </p>

          </div>

          <div className="question-box">

            <input
              type="text"
              placeholder={
                repository
                  ? "Ask anything about this repository..."
                  : "Enter a GitHub repository URL first..."
              }
              value={question}
              onChange={(event) =>
                setQuestion(
                  event.target.value
                )
              }
              onKeyDown={
                handleQuestionKeyDown
              }
            />

            <button
              onClick={askQuestion}
              disabled={
                asking ||
                !question.trim() ||
                !repoUrl.trim()
              }
            >
              {asking
                ? "Thinking..."
                : "Ask AI"}
            </button>

          </div>

          {!repoUrl.trim() && (
            <div className="ask-hint">
              Enter a GitHub repository URL
              to enable AI-powered questions.
            </div>
          )}

          {questionError && (
            <div className="error">
              {questionError}
            </div>
          )}

          {/* -------------------------------------- */}
          {/* AI Answer */}
          {/* -------------------------------------- */}

          {answer && (

            <div className="answer-section">

              <div className="answer-header">

                <span className="ai-badge">
                  AI
                </span>

                <h3>
                  AI Answer
                </h3>

              </div>

              <div className="answer-content">
                {answer}
              </div>

              {/* ---------------------------------- */}
              {/* Sources */}
              {/* ---------------------------------- */}

              {sources.length > 0 && (

                <div className="sources-section">

                  <h3>
                    Sources
                  </h3>

                  <div className="sources-list">

                    {sources.map(
                      (source, index) => (

                        <div
                          className="source-item"
                          key={`${source.file}-${index}`}
                        >

                          <div className="source-icon">
                            📄
                          </div>

                          <div className="source-info">

                            <strong>
                              {source.file}
                            </strong>

                            <span>
                              Lines{" "}
                              {source.start_line ??
                                "?"}{" "}
                              -{" "}
                              {source.end_line ??
                                "?"}
                              {" • "}
                              Similarity:{" "}
                              {typeof source.score ===
                              "number"
                                ? source.score.toFixed(
                                    4
                                  )
                                : "N/A"}
                            </span>

                          </div>

                        </div>

                      )
                    )}

                  </div>

                </div>

              )}

            </div>

          )}

        </section>

      </main>

      {/* -------------------------------------------- */}
      {/* Footer */}
      {/* -------------------------------------------- */}

      <footer className="footer">
        CodeForge AI • AI-powered codebase
        intelligence
      </footer>

    </div>
  );
}

export default App;