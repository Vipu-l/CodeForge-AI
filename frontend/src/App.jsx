import { useState } from "react";
import "./App.css";

function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [repository, setRepository] = useState(null);

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);

  const [loading, setLoading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  // Analyze GitHub repository
  const analyzeRepository = async () => {
    if (!repoUrl.trim()) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setLoading(true);
    setError("");
    setRepository(null);
    setAnswer(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/repositories/analyze?repo_url=${encodeURIComponent(
          repoUrl
        )}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to analyze repository."
        );
      }

      setRepository(data);
    } catch (error) {
      console.error("Repository analysis error:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  // Ask AI about the analyzed repository
  const askQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    if (!repository) {
      setError("Please analyze a repository first.");
      return;
    }

    setAsking(true);
    setError("");
    setAnswer(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/questions/ask?question=${encodeURIComponent(
          question
        )}&repository=${encodeURIComponent(repository.repository)}`,
        {
          method: "POST",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Failed to answer the question."
        );
      }

      setAnswer(data);
    } catch (error) {
      console.error("Ask AI error:", error);
      setError(error.message);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">

      {/* Navbar */}
      <header className="navbar">
        <div className="logo">
          CodeForge AI
        </div>

        <div className="nav-status">
          <span className="status-dot"></span>
          AI Code Intelligence
        </div>
      </header>

      <main className="container">

        {/* Error */}
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {/* Hero / Repository Input */}
        <section className="hero">

          <h1>
            Understand any codebase with AI.
          </h1>

          <p>
            Connect a public GitHub repository and
            explore its codebase using AI-powered
            semantic search and RAG.
          </p>

          <div className="repo-input">

            <input
              type="text"
              placeholder="https://github.com/username/repository"
              value={repoUrl}
              onChange={(event) =>
                setRepoUrl(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  analyzeRepository();
                }
              }}
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

        </section>

        {/* Repository Dashboard */}
        {repository && (
          <section className="dashboard">

            {/* Repository Name */}
            <div className="repository-header">

              <div>
                <span className="label">
                  Repository
                </span>

                <h2>
                  {repository.repository}
                </h2>
              </div>

              <span className="analyzed-badge">
                ✓ Analyzed
              </span>

            </div>

            {/* Statistics */}
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

            {/* Repository Files */}
            <div className="files-section">

              <h3>
                Repository Files
              </h3>

              <div className="file-list">

                {repository.files.map(
                  (file, index) => (

                    <div
                      className="file-item"
                      key={index}
                    >

                      <span>
                        📄
                      </span>

                      <span>
                        {file}
                      </span>

                    </div>

                  )
                )}

              </div>

            </div>

            {/* Ask AI */}
            <div className="ask-section">

              <h3>
                Ask CodeForge AI
              </h3>

              <p>
                Ask questions about this repository.
                CodeForge AI will search the codebase
                and generate an answer using RAG.
              </p>

              <textarea
                value={question}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                placeholder="How does the API handle repository analysis?"
                disabled={asking}
              />

              <button
                className="ask-button"
                onClick={askQuestion}
                disabled={
                  asking ||
                  !question.trim()
                }
              >
                {asking
                  ? "Thinking..."
                  : "Ask AI"}
              </button>

            </div>

            {/* AI Answer */}
            {answer && (
              <div className="answer-section">

                <div className="answer-header">
                  <h3>
                    AI Answer
                  </h3>

                  <span className="ai-badge">
                    AI
                  </span>
                </div>

                <div className="answer-text">
                  {answer.answer}
                </div>

                {/* Sources */}
                {answer.sources &&
                  answer.sources.length > 0 && (

                    <div className="sources-section">

                      <h3>
                        Sources
                      </h3>

                      {answer.sources.map(
                        (source, index) => (

                          <div
                            className="source-item"
                            key={index}
                          >

                            <div className="source-file">
                              📄 {source.file}
                            </div>

                            <div className="source-details">

                              Lines{" "}
                              {source.start_line}
                              {" - "}
                              {source.end_line}

                              {source.score !==
                                undefined && (
                                <>
                                  {" • "}
                                  Similarity:{" "}
                                  {source.score.toFixed(
                                    4
                                  )}
                                </>
                              )}

                            </div>

                          </div>

                        )
                      )}

                    </div>

                  )}

              </div>
            )}

          </section>
        )}

      </main>

      <footer className="footer">
        CodeForge AI • AI-powered codebase intelligence
      </footer>

    </div>
  );
}

export default App;