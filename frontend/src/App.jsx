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
      setError(error.message || "Failed to analyze repository.");
    } finally {
      setLoading(false);
    }
  };

  // Ask question about repository
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
      setError(error.message || "Failed to get AI answer.");
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">

      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>CodeForge AI</h1>
          <p>
            AI-powered codebase intelligence platform
          </p>
        </div>
      </header>

      <main className="container">

        {/* Error Message */}
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {/* Analyze Repository */}
        <section className="card">

          <h2>Analyze Repository</h2>

          <p className="description">
            Enter a public GitHub repository URL to
            analyze its codebase.
          </p>

          <div className="input-row">

            <input
              type="text"
              placeholder="https://github.com/user/repository"
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
              className="primary-button"
              onClick={analyzeRepository}
              disabled={loading}
            >
              {loading
                ? "Analyzing..."
                : "Analyze Repository"}
            </button>

          </div>

        </section>

        {/* Repository Results */}
        {repository && (
          <section className="card">

            <div className="repository-header">

              <div>
                <h2>{repository.repository}</h2>

                <p className="description">
                  Repository analysis completed
                  successfully.
                </p>
              </div>

            </div>

            {/* Statistics */}
            <div className="stats">

              <div className="stat-card">
                <span className="stat-number">
                  {repository.total_files}
                </span>

                <span className="stat-label">
                  Total Files
                </span>
              </div>

              <div className="stat-card">
                <span className="stat-number">
                  {repository.source_files}
                </span>

                <span className="stat-label">
                  Source Files
                </span>
              </div>

            </div>

            {/* Files */}
            <div className="files-section">

              <h3>Files</h3>

              <div className="file-list">

                {repository.files.map(
                  (file, index) => (

                    <div
                      className="file-item"
                      key={index}
                    >
                      {file}
                    </div>

                  )
                )}

              </div>

            </div>

          </section>
        )}

        {/* Ask CodeForge */}
        <section className="card">

          <h2>Ask CodeForge</h2>

          <p className="description">
            Ask questions about the analyzed
            repository and get answers based on
            its source code.
          </p>

          <textarea
            className="question-input"
            placeholder={
              repository
                ? "How does the API handle repository analysis?"
                : "Analyze a repository first..."
            }
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            disabled={!repository || asking}
          />

          <button
            className="primary-button ask-button"
            onClick={askQuestion}
            disabled={
              !repository ||
              !question.trim() ||
              asking
            }
          >
            {asking
              ? "Thinking..."
              : "Ask AI"}
          </button>

        </section>

        {/* AI Answer */}
        {answer && (
          <section className="card answer-card">

            <h2>AI Answer</h2>

            <div className="answer-text">
              {answer.answer}
            </div>

            {/* Sources */}
            {answer.sources &&
              answer.sources.length > 0 && (

                <div className="sources-section">

                  <h3>Sources</h3>

                  {answer.sources.map(
                    (source, index) => (

                      <div
                        className="source-item"
                        key={index}
                      >

                        <div className="source-file">
                          {source.file}
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

          </section>
        )}

      </main>

      {/* Footer */}
      <footer className="footer">
        <p>
          CodeForge AI • AI-powered codebase
          intelligence
        </p>
      </footer>

    </div>
  );
}

export default App;