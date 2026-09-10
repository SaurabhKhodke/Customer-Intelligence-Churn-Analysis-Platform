import React, { useState } from 'react';
import {
  BrainCircuit,
  Send,
  Sparkles,
  Database,
  FileText,
  ChevronDown,
  Loader2,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { askAIQuery } from '../services/api';
import ErrorMessage from '../components/ErrorMessage';


// ============================================================
// Helper: format source paths
// ============================================================

const getFilename = (sourcePath) => {
  if (!sourcePath) return 'unknown_source.md';

  const parts = sourcePath.split(/[/\\]/);

  return parts[parts.length - 1];
};


// ============================================================
// Helper: format SHAP feature names
// ============================================================

const formatFeatureName = (feature) => {
  if (!feature) return 'Unknown feature';

  return feature
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
};


// ============================================================
// Helper: format SHAP value
// ============================================================

const formatShapValue = (value) => {
  if (value === null || value === undefined) {
    return 'N/A';
  }

  const numericValue = Number(value);

  if (Number.isNaN(numericValue)) {
    return 'N/A';
  }

  return `${numericValue >= 0 ? '+' : ''}${numericValue.toFixed(4)}`;
};


// ============================================================
// SHAP explanation card
// ============================================================

const ShapExplanation = ({ result }) => {

  if (
    !result ||
    !result.shap_required ||
    !result.shap_success ||
    !result.shap_explanations ||
    result.shap_explanations.length === 0
  ) {
    return null;
  }


  return (
    <div
      className="mt-4"
      style={{
        padding: '1.25rem',
        borderRadius: '10px',
        border: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-main)'
      }}
    >

      {/* ---------------------------------------------------- */}
      {/* Header */}
      {/* ---------------------------------------------------- */}

      <div
        className="flex items-center gap-2 mb-3"
        style={{
          color: '#7c3aed',
          fontSize: '0.85rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          fontWeight: 600
        }}
      >
        <Sparkles size={16} />

        MODEL EXPLANATION
      </div>


      {/* ---------------------------------------------------- */}
      {/* Customer */}
      {/* ---------------------------------------------------- */}

      {result.shap_customer_id && (
        <div
          className="mb-3"
          style={{
            fontSize: '0.9rem',
            color: 'var(--text-secondary)'
          }}
        >
          <strong style={{ color: 'var(--text-primary)' }}>
            Customer:
          </strong>{' '}
          {result.shap_customer_id}
        </div>
      )}


      {/* ---------------------------------------------------- */}
      {/* Explanation */}
      {/* ---------------------------------------------------- */}

      <p
        className="text-muted mb-4"
        style={{
          fontSize: '0.85rem',
          lineHeight: '1.5'
        }}
      >
        These are the strongest factors that influenced the
        model's churn prediction for this customer.
        SHAP values describe the model contribution of each
        feature; they do not prove that a feature caused the
        customer's behavior.
      </p>


      {/* ---------------------------------------------------- */}
      {/* SHAP cards */}
      {/* ---------------------------------------------------- */}

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '0.75rem'
        }}
      >

        {result.shap_explanations.map((item, index) => {

          const shapValue = Number(item.shap_value);

          const isPositive =
            !Number.isNaN(shapValue) &&
            shapValue > 0;

          const isNegative =
            !Number.isNaN(shapValue) &&
            shapValue < 0;


          return (
            <div
              key={`${item.feature}-${index}`}
              style={{
                backgroundColor: 'var(--bg-card, #ffffff)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '1rem'
              }}
            >

              {/* Feature name */}

              <div
                style={{
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  color: 'var(--text-primary)',
                  marginBottom: '0.5rem'
                }}
              >
                {formatFeatureName(item.feature)}
              </div>


              {/* Observed value */}

              <div
                style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  marginBottom: '0.75rem'
                }}
              >
                Observed value:{' '}
                <strong style={{ color: 'var(--text-primary)' }}>
                  {item.value !== null &&
                  item.value !== undefined
                    ? String(item.value)
                    : 'N/A'}
                </strong>
              </div>


              {/* SHAP value */}

              <div
                style={{
                  fontSize: '1.15rem',
                  fontWeight: 700,
                  marginBottom: '0.4rem'
                }}
              >
                {formatShapValue(item.shap_value)}
              </div>


              {/* Direction */}

              <div
                className="flex items-center gap-1"
                style={{
                  fontSize: '0.78rem',
                  fontWeight: 500,
                  color: isPositive
                    ? '#b91c1c'
                    : isNegative
                      ? '#047857'
                      : 'var(--text-secondary)'
                }}
              >

                {isPositive && (
                  <TrendingUp size={14} />
                )}

                {isNegative && (
                  <TrendingDown size={14} />
                )}

                {!isPositive && !isNegative && (
                  <span>•</span>
                )}

                <span>
                  {item.direction || 'No directional information'}
                </span>

              </div>

            </div>
          );
        })}

      </div>


      {/* ---------------------------------------------------- */}
      {/* Interpretation note */}
      {/* ---------------------------------------------------- */}

      <div
        style={{
          marginTop: '1rem',
          padding: '0.75rem',
          borderRadius: '6px',
          backgroundColor: 'var(--bg-main)',
          border: '1px solid var(--border-color)',
          fontSize: '0.78rem',
          lineHeight: '1.5',
          color: 'var(--text-secondary)'
        }}
      >
        <strong style={{ color: 'var(--text-primary)' }}>
          How to read this:
        </strong>{' '}
        Positive SHAP values indicate that the feature
        contributed toward higher predicted churn risk.
        Negative values indicate a contribution toward lower
        predicted churn risk.
      </div>

    </div>
  );
};


// ============================================================
// MAIN COMPONENT
// ============================================================

const AIInsights = () => {

  const [query, setQuery] = useState('');

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState(null);

  const [result, setResult] = useState(null);


  // ==========================================================
  // Suggested questions
  // ==========================================================

  const suggestedQuestions = [
    "Why is customer 193228 high risk?",
    "What are the major drivers of churn?",
    "Which customers should we prioritize?",
    "Why is customer 180005 high risk compared to a typical customer?"
  ];
  

  // ==========================================================
  // Submit query
  // ==========================================================

  const handleSubmit = async (
    e,
    customQuery = null
  ) => {

    if (e) {
      e.preventDefault();
    }


    const questionToAsk =
      customQuery !== null
        ? customQuery
        : query;


    const trimmedQuery =
      questionToAsk.trim();


    if (!trimmedQuery) {

      setError(
        "Please enter a question."
      );

      return;
    }


    if (customQuery !== null) {

      setQuery(
        customQuery
      );
    }


    setLoading(true);

    setError(null);

    setResult(null);


    try {

      const response =
        await askAIQuery(
          trimmedQuery
        );

      setResult(
        response
      );

    } catch (err) {

      console.error(err);

      setError(
        "Unable to generate an AI insight. Please try again."
      );

    } finally {

      setLoading(false);

    }
  };


  // ==========================================================
  // Suggested question click
  // ==========================================================

  const handleSuggestedClick = (q) => {

    handleSubmit(
      null,
      q
    );

  };


  // ==========================================================
  // Render
  // ==========================================================

  return (

    <div
      style={{
        maxWidth: '800px',
        margin: '0 auto',
        paddingBottom: '3rem'
      }}
    >

      {/* ==================================================== */}
      {/* Header */}
      {/* ==================================================== */}

      <div className="text-center mb-4 mt-2">

        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            backgroundColor: '#f0fdfa',
            marginBottom: '1rem'
          }}
        >

          <BrainCircuit
            size={32}
            style={{
              color: '#0f766e'
            }}
          />

        </div>


        <h1
          style={{
            fontSize: '1.75rem',
            marginBottom: '0.5rem'
          }}
        >
          AI Customer Intelligence
        </h1>


        <p className="text-muted">
          Ask questions about customers, churn, risk
          segments and business behavior.
        </p>

      </div>


      {/* ==================================================== */}
      {/* Query box */}
      {/* ==================================================== */}

      <div
        className="card mb-4"
        style={{
          padding: '2rem'
        }}
      >

        <form
          onSubmit={(e) =>
            handleSubmit(e)
          }
          style={{
            position: 'relative'
          }}
        >

          <input
            type="text"
            className="form-control"
            placeholder="Ask your question..."
            value={query}

            onChange={(e) => {

              setQuery(
                e.target.value
              );

              if (
                error &&
                !e.target.value.trim()
              ) {

                setError(null);

              }

            }}

            disabled={loading}

            style={{
              paddingRight: '140px',
              height: '54px',
              fontSize: '1.1rem',
              borderRadius: '27px',
              paddingLeft: '1.5rem',
              borderColor: 'var(--primary)'
            }}
          />


          <button
            type="submit"
            className="btn btn-primary"

            style={{
              position: 'absolute',
              right: '6px',
              top: '6px',
              height: '42px',
              borderRadius: '21px',
              padding: '0 1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}

            disabled={
              loading ||
              !query.trim()
            }
          >

            {loading ? (

              <>
                Analyzing...
                <Loader2
                  size={16}
                  className="spin"
                />
              </>

            ) : (

              <>
                Ask AI
                <Send size={16} />
              </>

            )}

          </button>

        </form>

      </div>


      {/* ==================================================== */}
      {/* Suggested Questions */}
      {/* ==================================================== */}

      {!result &&
        !loading && (

          <div className="mb-4">

            <h3
              className="text-muted mb-3"
              style={{
                fontSize: '0.85rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 600
              }}
            >
              Suggested Questions
            </h3>


            <div
              className="grid-cols-2 gap-4"
            >

              {suggestedQuestions.map(
                (q, idx) => (

                  <button
                    key={idx}
                    className="card mb-0"

                    style={{
                      textAlign: 'left',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      transition:
                        'transform 0.2s, box-shadow 0.2s'
                    }}

                    onClick={() =>
                      handleSuggestedClick(q)
                    }

                    disabled={loading}
                  >

                    <Sparkles
                      size={18}
                      style={{
                        color: 'var(--primary)',
                        flexShrink: 0,
                        marginTop: '2px'
                      }}
                    />

                    <span
                      style={{
                        fontSize: '0.95rem'
                      }}
                    >
                      {q}
                    </span>

                  </button>

                )
              )}

            </div>

          </div>

        )
      }


      {/* ==================================================== */}
      {/* Error */}
      {/* ==================================================== */}

      {error && (
        <ErrorMessage
          message={error}
        />
      )}


      {/* ==================================================== */}
      {/* Result */}
      {/* ==================================================== */}

      {result && (

        <div
          className="card mt-4"
          style={{
            padding: '2rem'
          }}
        >

          {/* ------------------------------------------------ */}
          {/* AI Answer */}
          {/* ------------------------------------------------ */}

          <h2
            className="card-title mb-4 pb-2 flex items-center gap-2"
            style={{
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >

            <Sparkles
              size={20}
              className="text-primary"
            />

            AI INSIGHT

          </h2>


          <div
            className="ai-markdown-content"
            style={{
              fontSize: '1rem',
              lineHeight: '1.6',
              color: 'var(--text-primary)',
              marginBottom: '2rem'
            }}
          >

            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
            >
              {result.answer}
            </ReactMarkdown>

          </div>


          {/* ------------------------------------------------ */}
          {/* SHAP MODEL EXPLANATION */}
          {/* ------------------------------------------------ */}

          <ShapExplanation
            result={result}
          />


          {/* ------------------------------------------------ */}
          {/* Analysis details */}
          {/* ------------------------------------------------ */}

          <hr
            style={{
              margin: '2rem 0',
              borderColor: 'var(--border-color)'
            }}
          />


          <div>

            <h3
              className="text-muted mb-3 flex items-center gap-2"
              style={{
                fontSize: '0.85rem',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                fontWeight: 600
              }}
            >
              ANALYSIS DETAILS
            </h3>


            <div
              className="flex gap-4 mb-4 text-muted"
              style={{
                fontSize: '0.85rem'
              }}
            >

              <span>

                <strong
                  style={{
                    color: 'var(--text-primary)'
                  }}
                >
                  Intent:
                </strong>{' '}

                {result.intent}

              </span>


              {result.intent !== 'SQL' && (

                <span>

                  <strong
                    style={{
                      color: 'var(--text-primary)'
                    }}
                  >
                    Knowledge retrieved:
                  </strong>{' '}

                  {result.retrieved_documents || 0}

                </span>

              )}


              {result.intent !== 'RAG' && (

                <span>

                  <strong
                    style={{
                      color: 'var(--text-primary)'
                    }}
                  >
                    SQL executed:
                  </strong>{' '}

                  {result.sql_success
                    ? 'Yes'
                    : 'No'}

                </span>

              )}


              {result.shap_required && (

                <span>

                  <strong
                    style={{
                      color: 'var(--text-primary)'
                    }}
                  >
                    Model explanation:
                  </strong>{' '}

                  {result.shap_success
                    ? 'Yes'
                    : 'Unavailable'}

                </span>

              )}

            </div>


            {/* ============================================== */}
            {/* SQL */}
            {/* ============================================== */}

            {(result.intent === 'SQL' ||
              result.intent === 'BOTH') && (

              <div className="mt-4">

                <h4
                  className="flex items-center gap-2 mb-3"
                  style={{
                    fontSize: '0.85rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: '#1d4ed8'
                  }}
                >

                  <Database size={16} />

                  DATA ANALYSIS

                </h4>


                {result.sql_result &&
                  result.sql_result.success &&
                  result.sql_result.columns && (

                    <div className="mb-4">

                      {result.sql_result.rows &&
                      result.sql_result.rows.length > 0 ? (

                        <div
                          style={{
                            overflowX: 'auto'
                          }}
                        >

                          <table
                            className="table"
                            style={{
                              fontSize: '0.85rem',
                              marginBottom: 0
                            }}
                          >

                            <thead>

                              <tr>

                                {result.sql_result.columns.map(
                                  (col, idx) => (

                                    <th key={idx}>
                                      {col}
                                    </th>

                                  )
                                )}

                              </tr>

                            </thead>


                            <tbody>

                              {result.sql_result.rows.map(
                                (row, rowIdx) => (

                                  <tr key={rowIdx}>

                                    {result.sql_result.columns.map(
                                      (col, colIdx) => (

                                        <td key={colIdx}>

                                          {row[col] !== null
                                            ? String(row[col])
                                            : 'NULL'}

                                        </td>

                                      )
                                    )}

                                  </tr>

                                )
                              )}

                            </tbody>

                          </table>

                        </div>

                      ) : (

                        <div
                          className="text-muted p-2 text-center"
                          style={{
                            backgroundColor: '#f8fafc',
                            borderRadius: '6px',
                            border: '1px solid #e2e8f0',
                            fontSize: '0.85rem'
                          }}
                        >
                          No matching records found.
                        </div>

                      )}

                    </div>

                  )
                }


                {result.sql && (

                  <details
                    style={{
                      fontSize: '0.85rem'
                    }}
                  >

                    <summary
                      style={{
                        cursor: 'pointer',
                        fontWeight: 500,
                        color: 'var(--primary)',
                        outline: 'none'
                      }}
                    >

                      View generated SQL

                      <ChevronDown
                        size={14}
                        style={{
                          display: 'inline',
                          verticalAlign: 'middle'
                        }}
                      />

                    </summary>


                    <pre
                      style={{
                        backgroundColor: '#1e293b',
                        color: '#e2e8f0',
                        padding: '1rem',
                        borderRadius: '6px',
                        marginTop: '0.5rem',
                        overflowX: 'auto',
                        margin: '0.5rem 0 0 0'
                      }}
                    >

                      <code>
                        {result.sql}
                      </code>

                    </pre>

                  </details>

                )}

              </div>

            )}


            {/* ============================================== */}
            {/* BOTH separator */}
            {/* ============================================== */}

            {result.intent === 'BOTH' && (

              <hr
                style={{
                  margin: '1.5rem 0',
                  borderColor: 'var(--border-color)'
                }}
              />

            )}


            {/* ============================================== */}
            {/* Knowledge sources */}
            {/* ============================================== */}

            {(result.intent === 'RAG' ||
              result.intent === 'BOTH') && (

              <div
                className={
                  result.intent === 'RAG'
                    ? 'mt-4'
                    : ''
                }
              >

                <h4
                  className="flex items-center gap-2 mb-3"
                  style={{
                    fontSize: '0.85rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    color: '#047857'
                  }}
                >

                  <FileText size={16} />

                  KNOWLEDGE SOURCES

                </h4>


                {result.sources &&
                result.sources.length > 0 ? (

                  <ul
                    style={{
                      margin: 0,
                      paddingLeft: '1.5rem',
                      color: 'var(--text-secondary)',
                      fontSize: '0.85rem'
                    }}
                  >

                    {Array.from(
                      new Set(result.sources)
                    ).map(
                      (source, idx) => (

                        <li
                          key={idx}
                          style={{
                            marginBottom: '0.25rem'
                          }}
                        >
                          {getFilename(source)}
                        </li>

                      )
                    )}

                  </ul>

                ) : (

                  <span
                    className="text-muted"
                    style={{
                      fontSize: '0.85rem'
                    }}
                  >
                    No sources retrieved.
                  </span>

                )}

              </div>

            )}

          </div>

        </div>

      )}


      {/* ==================================================== */}
      {/* Markdown styles */}
      {/* ==================================================== */}

      <style>{`

        .ai-markdown-content h1,
        .ai-markdown-content h2,
        .ai-markdown-content h3 {
          margin-top: 1.5rem;
          margin-bottom: 0.75rem;
          color: var(--text-primary);
          font-weight: 600;
        }

        .ai-markdown-content h1 {
          font-size: 1.5rem;
        }

        .ai-markdown-content h2 {
          font-size: 1.25rem;
        }

        .ai-markdown-content h3 {
          font-size: 1.1rem;
        }

        .ai-markdown-content p {
          margin-bottom: 1rem;
        }

        .ai-markdown-content ul,
        .ai-markdown-content ol {
          margin-bottom: 1rem;
          padding-left: 1.5rem;
        }

        .ai-markdown-content li {
          margin-bottom: 0.25rem;
        }

        .ai-markdown-content strong {
          color: var(--text-primary);
          font-weight: 600;
        }

        .ai-markdown-content blockquote {
          border-left: 4px solid var(--border-color);
          padding-left: 1rem;
          color: var(--text-muted);
          margin-left: 0;
          margin-right: 0;
          background-color: var(--bg-main);
          padding-top: 0.5rem;
          padding-bottom: 0.5rem;
          border-radius: 0 4px 4px 0;
        }

        .ai-markdown-content code {
          background-color: var(--bg-main);
          padding: 0.2rem 0.4rem;
          border-radius: 4px;
          font-size: 0.9em;
          font-family: monospace;
          border: 1px solid var(--border-color);
        }

        .ai-markdown-content pre {
          background-color: #1e293b;
          color: #e2e8f0;
          padding: 1rem;
          border-radius: 6px;
          overflow-x: auto;
          margin-bottom: 1rem;
        }

        .ai-markdown-content pre code {
          background-color: transparent;
          padding: 0;
          border: none;
          color: inherit;
        }

        .ai-markdown-content table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }

        .ai-markdown-content th,
        .ai-markdown-content td {
          border: 1px solid var(--border-color);
          padding: 0.75rem;
          text-align: left;
        }

        .ai-markdown-content th {
          background-color: var(--bg-main);
          font-weight: 600;
          color: var(--text-primary);
        }

        .ai-markdown-content tr:nth-child(even) {
          background-color: #fafafa;
        }

        details > summary {
          list-style: none;
        }

        details > summary::-webkit-details-marker {
          display: none;
        }

        .spin {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }

          to {
            transform: rotate(360deg);
          }
        }

      `}</style>

    </div>

  );
};


export default AIInsights;
