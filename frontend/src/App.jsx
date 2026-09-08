import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const SUPPORTED_LANGUAGES = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
];


const ANALYSIS_MESSAGES = [
    "Scanning your codebase...",
    "Understanding your project structure...",
    "Detecting programming languages...",
    "Inspecting functions and classes...",
    "Finding potential code issues...",
    "Calculating project health...",
    "Building your code intelligence report...",
];
function App() {

    const getSourceCodeText = () => {
    if (sourceLines.length === 0) {
        return "";
    }

    return sourceLines
        .map((line) => line.code ?? "")
        .join("\n");
    };
    // =========================================================
    // ANALYSIS INPUT
    // =========================================================

    const [path, setPath] = useState("");
    const [zipFile, setZipFile] = useState(null);
    const [githubUrl, setGithubUrl] = useState("");

    // =========================================================
    // ANALYSIS DATA
    // =========================================================

    const [result, setResult] = useState(null);
    const [history, setHistory] = useState([]);

    // =========================================================
    // LOADING
    // =========================================================

    const [loading, setLoading] = useState(false);
    const [historyLoading, setHistoryLoading] = useState(false);
    const [githubLoading, setGithubLoading] = useState(false);
    const [analysisStatus, setAnalysisStatus] = useState("");
    const [analysisMessageIndex, setAnalysisMessageIndex] = useState(0);
    // =========================================================
    // ERRORS
    // =========================================================

    const [error, setError] = useState("");

    // =========================================================
    // INSPECTOR
    // =========================================================

    const [selectedFunction, setSelectedFunction] = useState(null);
    const [selectedIssue, setSelectedIssue] = useState(null);

    // =========================================================
    // SOURCE
    // =========================================================

    const [source, setSource] = useState(null);
    const [sourceLoading, setSourceLoading] = useState(false);
    const [sourceError, setSourceError] = useState("");

const sourceLines = useMemo(() => {
    if (!source) {
        return [];
    }

    // =========================================================
    // Backend response:
    // {
    //     source: [
    //         {
    //             line: 7,
    //             code: "print()",
    //             is_target: true
    //         }
    //     ]
    // }
    // =========================================================

    const lines = source.source ?? source.lines;

    if (Array.isArray(lines)) {
        return lines.map((line, index) => {
            // Support plain string lines
            if (typeof line === "string") {
                const lineNumber =
                    (Number(source.start_line) || 1) + index;

                return {
                    line: lineNumber,
                    code: line,
                    is_target:
                        lineNumber ===
                        Number(
                            selectedIssue?.line ??
                            selectedFunction?.line
                        ),
                };
            }

            // Support object lines
            const lineNumber =
                line?.line ??
                (Number(source.start_line) || 1) + index;

            return {
                line: lineNumber,
                code:
                    line?.code ??
                    line?.source ??
                    line?.text ??
                    "",
                is_target:
                    line?.is_target ??
                    (
                        lineNumber ===
                        Number(
                            selectedIssue?.line ??
                            selectedFunction?.line
                        )
                    ),
            };
        });
    }

    

    // =========================================================
    // Fallback for APIs that return raw source code
    // =========================================================

    const rawCode =
        source.source_code ??
        source.code ??
        source.content ??
        "";

    if (
        typeof rawCode !== "string" ||
        !rawCode.trim()
    ) {
        return [];
    }

    const startLine =
        Number(source.start_line) || 1;

    const targetLine = Number(
        selectedIssue?.line ??
        selectedFunction?.line
    );

    return rawCode
        .replace(/\r\n/g, "\n")
        .split("\n")
        .map((code, index) => {
            const lineNumber =
                startLine + index;

            return {
                line: lineNumber,
                code,
                is_target:
                    lineNumber === targetLine,
            };
        });
}, [
    source,
    selectedIssue,
    selectedFunction,
]);

    // =========================================================
    // AI
    // =========================================================

    const [aiExplanation, setAiExplanation] = useState("");
    const [aiLoading, setAiLoading] = useState(false);
    const [aiError, setAiError] = useState("");

    const [aiFixLoading, setAiFixLoading] = useState(false);
    const [aiFixError, setAiFixError] = useState("");
    const [aiFix, setAiFix] = useState("");

    // =========================================================
    // ISSUE FILTER
    // =========================================================

    const [issueFilter, setIssueFilter] = useState("ALL");
    const [issueSearch, setIssueSearch] = useState("");

    const [showAllIssues, setShowAllIssues] = useState(false);

    // =========================================================
    // HISTORICAL ANALYSIS
    // =========================================================

    const [selectedAnalysis, setSelectedAnalysis] = useState(null);

    // =========================================================
    // LOAD HISTORY
    // =========================================================

    const loadHistory = async () => {
        setHistoryLoading(true);

        try {
            const response = await axios.get(
                `${API_BASE}/api/v1/analysis`
            );

            setHistory(
                Array.isArray(response.data)
                    ? response.data
                    : []
            );
        } catch (err) {
            console.error(
                "Unable to load analysis history.",
                err
            );

            setError(
                err.response?.data?.detail ||
                    "Unable to load analysis history."
            );
        } finally {
            setHistoryLoading(false);
        }
    };

    // =========================================================
    // INITIAL LOAD
    // =========================================================

    useEffect(() => {
        loadHistory();
    }, []);

    // =========================================================
// ANALYSIS MESSAGE ROTATION
// =========================================================

useEffect(() => {
    if (!loading && !githubLoading) {
        return;
    }

    setAnalysisMessageIndex(0);

    const interval = window.setInterval(() => {
        setAnalysisMessageIndex((current) => {
            return (current + 1) % ANALYSIS_MESSAGES.length;
        });
    }, 1500);

    return () => {
        window.clearInterval(interval);
    };
}, [loading, githubLoading]);

    // =========================================================
    // RESET INSPECTOR
    // =========================================================

    const resetInspector = () => {
        setSelectedFunction(null);
        setSelectedIssue(null);

        setSource(null);
        setSourceError("");

        setAiExplanation("");
        setAiError("");

        setAiFix("");
        setAiFixError("");
    };

    // =========================================================
    // ANALYZE LOCAL PROJECT
    // =========================================================

    const analyzeProject = async () => {
        if (!path.trim()) {
            setAnalysisStatus("");
            setError("Please enter a project path.");
            return;
        }

        setLoading(true);
        setError("");
        

        setResult(null);
        setSelectedAnalysis(null);
        setShowAllIssues(false);

        resetInspector();

        try {
            const response = await axios.post(
                `${API_BASE}/api/v1/analyze`,
                {
                    path: path.trim(),
                }
            );

            setResult(response.data);
            

            await loadHistory();
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.detail ||
                    "Unable to analyze project."
            );
        } finally {
            setLoading(false);  
        }
    };

    // =========================================================
    // UPLOAD ZIP
    // =========================================================

    const uploadProject = async () => {
        if (!zipFile) {
            setError("Please select a ZIP file.");
            return;
        }

        setLoading(true);
        setError("");
       

        setResult(null);
        setSelectedAnalysis(null);
        setShowAllIssues(false);

        resetInspector();

        try {
            const formData = new FormData();

            formData.append("file", zipFile);

            const response = await axios.post(
                `${API_BASE}/api/v1/analyze/upload`,
                formData
            );

            setResult(response.data);
            

            await loadHistory();
        } catch (err) {
            console.error(err);

            setError(
                err.response?.data?.detail ||
                    "Unable to analyze ZIP file."
            );
        } finally {
            setLoading(false);
        }
    };

    // =========================================================
    // GITHUB ANALYSIS
    // =========================================================

    const analyzeGithub = async () => {
        if (!githubUrl.trim()) {
            setError("Please enter a GitHub repository URL.");
            return;
        }

        setGithubLoading(true);
        setError("");
        ;

        setResult(null);
        setSelectedAnalysis(null);
        setShowAllIssues(false);

        resetInspector();

        try {
            /*
             * Expected backend endpoint:
             *
             * POST /api/v1/analyze/github
             *
             * body:
             * {
             *     url: githubUrl
             * }
             */

            const response = await axios.post(
                `${API_BASE}/api/v1/analyze/github`,
                {
                    url: githubUrl.trim(),
                }
            );

            setResult(response.data);
            

            await loadHistory();
        } catch (err) {
            setAnalysisStatus("");
            console.error(err);

            setError(
                err.response?.data?.detail ||
                    "Unable to analyze GitHub repository."
            );
        } finally {
            setGithubLoading(false);
        }
    };

    // =========================================================
// LOAD SOURCE
// =========================================================

const loadSource = async (
    item,
    type = "function"
) => {
    if (
    !item?.file ||
    item?.line === undefined ||
    item?.line === null
) {
        setSourceError(
            "Source information is missing for this item."
        );
        return;
    }

    // Open inspector immediately
    if (type === "function") {
        setSelectedFunction(item);
        setSelectedIssue(null);
    } else {
        setSelectedIssue(item);
        setSelectedFunction(null);
    }

    // Reset previous source / AI state
    setSource(null);
    setSourceError("");

    setAiExplanation("");
    setAiError("");

    setAiFix("");
    setAiFixError("");

    setSourceLoading(true);

    try {
        const response = await axios.get(
            `${API_BASE}/api/v1/source`,
            {
                params: {
                    file: item.file,
                    line: item.line,
                    context:
                        type === "function"
                            ? 10
                            : 7,
                },
            }
        );

        console.log(
            "SOURCE API RESPONSE:",
            response.data
        );

        // Keep the complete backend response
        setSource(response.data);

    } catch (err) {
        console.error(
            "Source loading error:",
            err
        );

        setSourceError(
            err.response?.data?.detail ||
                "Unable to load source code."
        );
    } finally {
        setSourceLoading(false);
    }
};
    // =========================================================
    // WORST FUNCTION
    // =========================================================

    const viewFunctionSource = (
        functionItem
    ) => {
        loadSource(
            functionItem,
            "function"
        );
    };

    // =========================================================
    // ISSUE
    // =========================================================

    const viewSource = (issue) => {
        loadSource(issue, "issue");
    };

    // =========================================================
    // CLOSE INSPECTOR
    // =========================================================

    const closeInspector = () => {
        resetInspector();
    };

    // Keep the current analysis position/state unchanged while the modal is open.
    useEffect(() => {
        const inspectorOpen = Boolean(
            selectedFunction || selectedIssue
        );

        if (!inspectorOpen) {
            return undefined;
        }

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";

        const handleEscape = (event) => {
            if (event.key === "Escape") {
                closeInspector();
            }
        };

        window.addEventListener("keydown", handleEscape);

        return () => {
            document.body.style.overflow = previousOverflow;
            window.removeEventListener("keydown", handleEscape);
        };
    }, [selectedFunction, selectedIssue]);

    // =========================================================
    // AI EXPLANATION
    // =========================================================

    const explainIssueWithAI = async () => {
        if (!selectedIssue) {
            setAiError("No issue selected.");
            return;
        }

        if (!source) {
            setAiError(
                "Source code is not loaded."
            );
            return;
        }

        try {
            setAiLoading(true);
            setAiError("");
            setAiExplanation("");

            const sourceCode = getSourceCodeText();

            if (
                !sourceCode ||
                !sourceCode.trim()
            ) {
                setAiError(
                    "Source code is empty."
                );
                return;
            }

            const response =
                await axios.post(
                    `${API_BASE}/api/v1/ai/explain`,
                    {
                        issue: selectedIssue,
                        source_code:
                            sourceCode,
                    }
                );

            setAiExplanation(
                response.data.explanation ||
                    "No explanation returned."
            );
        } catch (error) {
            console.error(
                "AI explanation error:",
                error
            );

            setAiError(
                error.response?.data
                    ?.detail ||
                    "Failed to get AI explanation."
            );
        } finally {
            setAiLoading(false);
        }
    };

    // =========================================================
    // AI FIX
    // =========================================================

    const suggestFixWithAI = async () => {
        if (
            !selectedIssue ||
            !source
        ) {
            return;
        }

        setAiFixLoading(true);
        setAiFixError("");
        setAiFix("");

        try {
            const sourceCode = getSourceCodeText();

            if (
                !sourceCode?.trim()
            ) {
                setAiFixError(
                    "Source code is empty."
                );
                return;
            }

            const response =
                await fetch(
                    `${API_BASE}/api/v1/ai/fix`,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type":
                                "application/json",
                        },
                        body: JSON.stringify(
                            {
                                issue:
                                    selectedIssue,
                                source_code:
                                    sourceCode,
                            }
                        ),
                    }
                );

            const data =
                await response.json();

            if (!response.ok) {
                throw new Error(
                    data.detail ||
                        "Failed to generate fix."
                );
            }

            setAiFix(
                data.fix ||
                    "No fix was generated."
            );
        } catch (error) {
            console.error(
                "AI fix error:",
                error
            );

            setAiFixError(
                error.message ||
                    "Unable to generate AI fix."
            );
        } finally {
            setAiFixLoading(false);
        }
    };

    // =========================================================
    // HISTORICAL ANALYSIS
    // =========================================================

    const viewHistoricalAnalysis = (
        analysis
    ) => {
        if (!analysis) {
            return;
        }

        setSelectedAnalysis(
            analysis
        );

        resetInspector();

        setTimeout(() => {
            const element =
                document.getElementById(
                    "historical-details"
                );

            if (element) {
                element.scrollIntoView({
                    behavior:
                        "smooth",
                    block: "start",
                });
            }
        }, 100);
    };

    // =========================================================
    // DATE FORMAT
    // =========================================================

    const formatDate = (
        dateString
    ) => {
        if (!dateString) {
            return "Unknown";
        }

        try {
            return new Date(
                dateString
            ).toLocaleString();
        } catch {
            return "Unknown";
        }
    };

    // =========================================================
    // ALL ISSUES
    // =========================================================

    const allIssues = Array.isArray(
        result?.issues
    )
        ? result.issues
        : [];

    // =========================================================
    // FILTER ISSUES
    // =========================================================

    const filteredIssues = useMemo(() => {
        return allIssues.filter(
            (issue) => {
                const matchesFilter =
                    issueFilter ===
                        "ALL" ||
                    issue.severity ===
                        issueFilter;

                const searchText =
                    issueSearch
                        .trim()
                        .toLowerCase();

                const matchesSearch =
                    !searchText ||
                    issue.type
                        ?.toLowerCase()
                        .includes(
                            searchText
                        ) ||
                    issue.message
                        ?.toLowerCase()
                        .includes(
                            searchText
                        ) ||
                    issue.file
                        ?.toLowerCase()
                        .includes(
                            searchText
                        ) ||
                    issue.function
                        ?.toLowerCase()
                        .includes(
                            searchText
                        ) ||
                    issue.language
                        ?.toLowerCase()
                        .includes(
                            searchText
                        );

                return (
                    matchesFilter &&
                    matchesSearch
                );
            }
        );
    }, [
        allIssues,
        issueFilter,
        issueSearch,
    ]);

    // =========================================================
    // DISPLAYED ISSUES
    // =========================================================

    const displayedIssues =
        showAllIssues
            ? filteredIssues
            : filteredIssues.slice(
                  0,
                  10
              );

    // =========================================================
    // RESET ISSUE PAGINATION
    // =========================================================

    useEffect(() => {
        setShowAllIssues(false);
    }, [
        issueFilter,
        issueSearch,
    ]);

    // =========================================================
    // LANGUAGE DATA
    // =========================================================

    const languageData =
        result?.language_analysis ||
        result?.languages ||
        result?.language_report ||
        {};

    const getLanguageData = (language) => {
    // 1. Prefer explicitly prepared languageData
    const prepared = findLanguageData(
        languageData,
        language
    );

    if (prepared) {
        return prepared;
    }

    // 2. Read directly from backend language_stats
    const stats =
        result?.summary?.language_stats?.[language];

    const score =
        result?.health?.language_scores?.[language];

    if (stats) {
        return {
            ...stats,
            score:
                typeof score === "object"
                    ? score.score
                    : score,
            rating:
                typeof score === "object"
                    ? score.rating
                    : undefined,
        };
    }

    // 3. Last fallback: derive information from issues
    return buildLanguageIssueFallback(
        allIssues,
        language
    );
};

    // =========================================================
    // GITHUB DATA
    // =========================================================

    const githubData =
        result?.github_analysis ||
        result?.github ||
        null;

    // =========================================================
    // PROJECT NAME
    // =========================================================

    const projectName =
        result?.project_name ||
        result?.project ||
        result?.name ||
        "Project";

    // =========================================================
    // SOURCE LINES
    // =========================================================

   
    // =========================================================
    // RENDER
    // =========================================================

    return (
        <div className="app">

            {/* =====================================================
                HEADER
            ===================================================== */}

            <header className="header">

                <div className="logo">
                    Dev
                    <span>Pilot</span>
                </div>

                <div className="header-right">

                    <div className="status">
                        <span className="status-dot" />
                        Local Analyzer
                    </div>

                </div>

            </header>


            {/* =====================================================
                MAIN
            ===================================================== */}

            <main className="container">

                {/* =================================================
                    HERO
                ================================================= */}

                <section className="hero">

                    <p className="eyebrow">
                        CODE INTELLIGENCE PLATFORM
                    </p>

                    <h1>
                        Understand your
                        codebase.
                    </h1>

                    <p className="subtitle">
                        Analyze local projects,
                        GitHub repositories and
                        ZIP files. DevPilot
                        automatically detects
                        multiple programming
                        languages and evaluates
                        your entire codebase.
                    </p>


                    {/* =================================================
                        LOCAL PROJECT
                    ================================================= */}

                    <div className="analyze-box">

                        <div className="input-icon">
                            ⌘
                        </div>

                        <input
                            type="text"
                            placeholder="D:/path/to/your/project"
                            value={path}
                            onChange={(e) =>
                                setPath(
                                    e.target.value
                                )
                            }
                            onKeyDown={(e) => {
                                if (
                                    e.key ===
                                    "Enter"
                                ) {
                                    analyzeProject();
                                }
                            }}
                        />

                        <button
                            onClick={
                                analyzeProject
                            }
                            disabled={
                                loading ||
                                githubLoading
                            }
                        >
                            {loading
                                ? "Analyzing..."
                                : "Analyze Project"}
                        </button>

                    </div>


                    {/* =================================================
                        ZIP
                    ================================================= */}

                    <div className="source-options">

                        <div className="source-option">

                            <div className="source-option-title">
                                ZIP Project
                            </div>

                            <div className="source-option-description">
                                Upload a project
                                archive
                            </div>

                            <label className="file-input">

                                <input
                                    type="file"
                                    accept=".zip"
                                    onChange={(e) =>
                                        setZipFile(
                                            e.target
                                                .files?.[0] ||
                                                null
                                        )
                                    }
                                />

                                <span>
                                    Choose File
                                </span>

                            </label>

                            {zipFile && (
                                <small>
                                    {zipFile.name}
                                </small>
                            )}

                            <button
                                className="secondary-action"
                                onClick={
                                    uploadProject
                                }
                                disabled={
                                    loading ||
                                    !zipFile
                                }
                            >
                                {loading
                                    ? "Analyzing..."
                                    : "Analyze ZIP"}
                            </button>

                        </div>


                        {/* =================================================
                            GITHUB
                        ================================================= */}

                        <div className="source-option">

                            <div className="source-option-title">
                                GitHub Repository
                            </div>

                            <div className="source-option-description">
                                Analyze a public
                                repository
                            </div>

                            <input
                                className="github-input"
                                type="text"
                                placeholder="https://github.com/user/repository"
                                value={githubUrl}
                                onChange={(e) =>
                                    setGithubUrl(
                                        e.target.value
                                    )
                                }
                            />

                            <button
                                className="secondary-action"
                                onClick={
                                    analyzeGithub
                                }
                                disabled={
                                    githubLoading ||
                                    !githubUrl.trim()
                                }
                            >
                                {githubLoading
                                    ? "Analyzing..."
                                    : "Analyze GitHub"}
                            </button>

                        </div>

                    </div>
                     {/* =================================================
                       ANALYSIS STATUS OVERLAY
                   ================================================= */}

                   {(loading || githubLoading) && (
                       <div className="analysis-status-overlay">
                           <div
                               key={analysisMessageIndex}
                               className="analysis-status-text"
                           >
                               {ANALYSIS_MESSAGES[analysisMessageIndex]}
                           </div>
                       </div>
                   )}



                    {/* =================================================
                        ERROR
                    ================================================= */}

                    {(error || analysisStatus) && (
    <div
        className={
            error
                ? "analysis-message error"
                : "analysis-message"
        }
    >
        <div className="analysis-message-content">
            <span className="analysis-message-icon">
                {error ? "!" : "●"}
            </span>

            <div>
                <strong>
                    {error
                        ? "Analysis failed"
                        : "Analysis in progress"}
                </strong>

                <p>
                    {error || analysisStatus}
                </p>
            </div>
        </div>

        {error && (
            <button
                type="button"
                className="retry-button"
                onClick={() => {
                    setError("");
                    setAnalysisStatus("");
                }}
            >
                Dismiss
            </button>
        )}
    </div>
)}

                </section>


                {/* =====================================================
                    CURRENT ANALYSIS
                ===================================================== */}

                {result && (

                    <section className="dashboard">

                        {/* =================================================
                            ANALYSIS HEADER
                        ================================================= */}

                        <div className="analysis-heading">

                            <div>
                                <p className="eyebrow">
                                    ANALYSIS COMPLETE
                                </p>

                                <h2>
                                    Project Analysis
                                </h2>

                                <p>
                                    {projectName}
                                </p>
                            </div>

                            {githubData && (
                                <div className="github-analysis-badge">
                                    <span>●</span>
                                    GitHub Analysis
                                </div>
                            )}

                        </div>


                        {/* =================================================
                            HEALTH
                        ================================================= */}

                        <div className="health-card premium-health-card">

                            <div className="health-info">

                                <p className="card-label">
                                    PROJECT HEALTH
                                </p>

                                <h2>
                                    {
                                        result
                                            .health
                                            ?.score ??
                                        0
                                    }
                                    <span>
                                        /100
                                    </span>
                                </h2>

                                <p className="rating">
                                    {
                                        result
                                            .health
                                            ?.rating ||
                                        "UNKNOWN"
                                    }
                                </p>

                                <p className="health-description">
                                    Overall code
                                    quality based
                                    on detected
                                    issues,
                                    complexity
                                    and security
                                    risks.
                                </p>

                            </div>


                            <div className="health-ring">

                                <svg
                                    viewBox="0 0 120 120"
                                    className="health-svg"
                                >

                                    <circle
                                        className="health-ring-bg"
                                        cx="60"
                                        cy="60"
                                        r="50"
                                    />

                                    <circle
                                        className="health-ring-progress"
                                        cx="60"
                                        cy="60"
                                        r="50"
                                        style={{
                                            strokeDasharray:
                                                314,
                                            strokeDashoffset:
                                                314 -
                                                (314 *
                                                    (result
                                                        .health
                                                        ?.score ??
                                                        0)) /
                                                    100,
                                        }}
                                    />

                                </svg>

                                <div className="health-ring-value">
                                    {
                                        result
                                            .health
                                            ?.score ??
                                        0
                                    }
                                </div>

                            </div>

                        </div>


                        {/* =================================================
                            METRICS
                        ================================================= */}

                        <div className="metrics">

                            <Metric
                                label="Files"
                                value={
                                    result
                                        .summary
                                        ?.total_files ??
                                    0
                                }
                            />

                            <Metric
                                label="Lines"
                                value={
                                    result
                                        .summary
                                        ?.total_lines ??
                                    0
                                }
                            />

                            <Metric
                                label="Functions"
                                value={
                                    result
                                        .summary
                                        ?.total_functions ??
                                    0
                                }
                            />

                            <Metric
                                label="Issues"
                                value={
                                    allIssues.length
                                }
                            />

                        </div>


                        {/* =================================================
                            LANGUAGE REPORT
                        ================================================= */}

                        <section className="panel language-panel">

                            <div className="panel-header">

                                <div>
                                    <p className="card-label">
                                        LANGUAGE INTELLIGENCE
                                    </p>

                                    <h3>
                                        Language-wise Report
                                    </h3>

                                    <p className="panel-subtitle">
                                        DevPilot detects and
                                        evaluates every
                                        supported language
                                        independently.
                                    </p>
                                </div>

                            </div>


                            <div className="language-grid">

                                {SUPPORTED_LANGUAGES.map(
                                    (language) => {
                                        const data =
                                            getLanguageData(
                                                language
                                            );

                                        return (
                                            <LanguageCard
                                                key={
                                                    language
                                                }
                                                language={
                                                    language
                                                }
                                                data={
                                                    data
                                                }
                                            />
                                        );
                                    }
                                )}

                            </div>

                        </section>


                        {/* =================================================
                            GITHUB REPORT
                        ================================================= */}

                        {githubData && (
                            <section className="panel github-panel">

                                <div className="panel-header">

                                    <div>
                                        <p className="card-label">
                                            GITHUB INTELLIGENCE
                                        </p>

                                        <h3>
                                            Repository Analysis
                                        </h3>

                                        <p className="panel-subtitle">
                                            Repository-level
                                            codebase insights.
                                        </p>
                                    </div>

                                </div>


                                <div className="github-grid">

                                    <div className="github-stat">
                                        <span>
                                            Repository
                                        </span>

                                        <strong>
                                            {
                                                githubData
                                                    .repository ||
                                                githubData
                                                    .repo_name ||
                                                githubData
                                                    .name ||
                                                githubUrl ||
                                                "Unknown"
                                            }
                                        </strong>
                                    </div>


                                    <div className="github-stat">
                                        <span>
                                            Branch
                                        </span>

                                        <strong>
                                            {
                                                githubData
                                                    .branch ||
                                                "main"
                                            }
                                        </strong>
                                    </div>


                                    <div className="github-stat">
                                        <span>
                                            Contributors
                                        </span>

                                        <strong>
                                            {
                                                githubData
                                                    .contributors ??
                                                0
                                            }
                                        </strong>
                                    </div>


                                    <div className="github-stat">
                                        <span>
                                            Commits
                                        </span>

                                        <strong>
                                            {
                                                githubData
                                                    .commits ??
                                                0
                                            }
                                        </strong>
                                    </div>

                                </div>

                            </section>
                        )}


                        {/* =================================================
                            ISSUE BREAKDOWN
                        ================================================= */}

                        <div className="dashboard-breakdown">

                            {/* SEVERITY */}

                            <section className="panel">

                                <div className="panel-header">

                                    <div>

                                        <h3>
                                            Issue Severity
                                        </h3>

                                        <p className="panel-subtitle">
                                            Issues grouped by
                                            severity
                                        </p>

                                    </div>

                                </div>


                                <div className="severity-grid">

                                    <div className="severity-card high">
                                        <span>
                                            HIGH
                                        </span>

                                        <strong>
                                            {
                                                result
                                                    .severity_counts
                                                    ?.HIGH ??
                                                0
                                            }
                                        </strong>
                                    </div>

                                    <div className="severity-card medium">
                                        <span>
                                            MEDIUM
                                        </span>

                                        <strong>
                                            {
                                                result
                                                    .severity_counts
                                                    ?.MEDIUM ??
                                                0
                                            }
                                        </strong>
                                    </div>

                                    <div className="severity-card low">
                                        <span>
                                            LOW
                                        </span>

                                        <strong>
                                            {
                                                result
                                                    .severity_counts
                                                    ?.LOW ??
                                                0
                                            }
                                        </strong>
                                    </div>

                                </div>

                            </section>


                            {/* ISSUE TYPES */}

                            <section className="panel">

                                <div className="panel-header">

                                    <div>

                                        <h3>
                                            Issue Categories
                                        </h3>

                                        <p className="panel-subtitle">
                                            Types of problems
                                            detected
                                        </p>

                                    </div>

                                </div>


                                <div className="issue-type-list">

                                    {Object.entries(
                                        result
                                            .issue_type_counts ||
                                            {}
                                    ).length ===
                                    0 ? (
                                        <p className="empty">
                                            No issue
                                            categories
                                            detected.
                                        </p>
                                    ) : (
                                        Object.entries(
                                            result
                                                .issue_type_counts ||
                                                {}
                                        )
                                            .sort(
                                                (
                                                    a,
                                                    b
                                                ) =>
                                                    b[1] -
                                                    a[1]
                                            )
                                            .map(
                                                ([
                                                    type,
                                                    count,
                                                ]) => (
                                                    <div
                                                        className="issue-type-row"
                                                        key={
                                                            type
                                                        }
                                                    >
                                                        <span>
                                                            {
                                                                type
                                                            }
                                                        </span>

                                                        <strong>
                                                            {
                                                                count
                                                            }
                                                        </strong>
                                                    </div>
                                                )
                                            )
                                    )}

                                </div>

                            </section>

                        </div>


                        {/* =================================================
                            TWO COLUMN
                        ================================================= */}

                        <div className="grid">

                            {/* WORST FUNCTIONS */}

                            <section className="panel">

                                <div className="panel-header">

                                    <div>

                                        <h3>
                                            Worst Functions
                                        </h3>

                                        <p className="panel-subtitle">
                                            Click a function
                                            to inspect its
                                            source code
                                        </p>

                                    </div>

                                </div>


                                {!result.worst_functions ||
                                result
                                    .worst_functions
                                    .length ===
                                    0 ? (

                                    <p className="empty">
                                        No problematic
                                        functions found.
                                    </p>

                                ) : (

                                    <div className="function-list">

                                        {result
                                            .worst_functions
                                            .map(
                                                (
                                                    functionItem,
                                                    index
                                                ) => (

                                                    <div
                                                        className="function-row clickable"
                                                        key={`${functionItem.file}-${functionItem.name}-${index}`}
                                                        onClick={() =>
                                                            viewFunctionSource(
                                                                functionItem
                                                            )
                                                        }
                                                    >

                                                        <div className="function-info">

                                                            <strong>
                                                                {
                                                                    functionItem.name
                                                                }
                                                            </strong>

                                                            <small>
                                                                {
                                                                    functionItem.file
                                                                }
                                                            </small>

                                                            <small>
                                                                Line{" "}
                                                                {
                                                                    functionItem.line
                                                                }
                                                            </small>

                                                        </div>


                                                        <div className="complexity-info">

                                                            <div className="complexity">
                                                                {
                                                                    functionItem.complexity
                                                                }
                                                            </div>

                                                            <small>
                                                                {
                                                                    functionItem.level
                                                                }
                                                            </small>

                                                        </div>

                                                    </div>

                                                )
                                            )}

                                    </div>

                                )}

                            </section>


                            {/* RECOMMENDATIONS */}

                            <section className="panel">

                                <div className="panel-header">

                                    <div>

                                        <h3>
                                            Recommendations
                                        </h3>

                                        <p className="panel-subtitle">
                                            Suggested improvements
                                            for your codebase
                                        </p>

                                    </div>

                                </div>


                                {!result.recommendations ||
                                result
                                    .recommendations
                                    .length ===
                                    0 ? (

                                    <p className="empty">
                                        No recommendations.
                                    </p>

                                ) : (

                                    result
                                        .recommendations
                                        .map(
                                            (
                                                recommendation,
                                                index
                                            ) => (

                                                <div
                                                    className="recommendation"
                                                    key={
                                                        index
                                                    }
                                                >

                                                    <span>
                                                        !
                                                    </span>

                                                    {
                                                        recommendation
                                                    }

                                                </div>

                                            )
                                        )

                                )}

                            </section>

                        </div>


                        {/* =================================================
                            ISSUES
                        ================================================= */}

                        <section className="panel issues-panel premium-issues-panel">

                            <div className="panel-header issues-header">

                                <div>

                                    <p className="card-label">
                                        CODE ISSUES
                                    </p>

                                    <h3>
                                        Issues
                                    </h3>

                                    <p className="panel-subtitle">
                                        Showing{" "}
                                        {Math.min(
                                            10,
                                            filteredIssues.length
                                        )}{" "}
                                        of{" "}
                                        {
                                            filteredIssues.length
                                        }{" "}
                                        matching issues
                                    </p>

                                </div>

                                <div className="issue-count">
                                    {
                                        filteredIssues.length
                                    }
                                </div>

                            </div>


                            {/* =================================================
                                TOOLBAR
                            ================================================= */}

                            <div className="issue-toolbar">

                                <div className="issue-search">

                                    <span>
                                        ⌕
                                    </span>

                                    <input
                                        type="text"
                                        placeholder="Search issues, files, functions..."
                                        value={
                                            issueSearch
                                        }
                                        onChange={(
                                            e
                                        ) =>
                                            setIssueSearch(
                                                e
                                                    .target
                                                    .value
                                            )
                                        }
                                    />

                                    {issueSearch && (
                                        <button
                                            className="clear-search"
                                            onClick={() =>
                                                setIssueSearch(
                                                    ""
                                                )
                                            }
                                        >
                                            ×
                                        </button>
                                    )}

                                </div>


                                <div className="issue-filters">

                                    {[
                                        "ALL",
                                        "HIGH",
                                        "MEDIUM",
                                        "LOW",
                                    ].map(
                                        (
                                            filter
                                        ) => (

                                            <button
                                                key={
                                                    filter
                                                }
                                                className={
                                                    issueFilter ===
                                                    filter
                                                        ? "issue-filter active"
                                                        : "issue-filter"
                                                }
                                                onClick={() =>
                                                    setIssueFilter(
                                                        filter
                                                    )
                                                }
                                            >
                                                {
                                                    filter
                                                }
                                            </button>

                                        )
                                    )}

                                </div>

                            </div>


                            {/* =================================================
                                ISSUE LIST
                            ================================================= */}

                            <div className="issue-list">

                                {displayedIssues.length ===
                                0 ? (

                                    <div className="issues-empty">

                                        <div className="empty-icon">
                                            ✓
                                        </div>

                                        <strong>
                                            No issues
                                            found
                                        </strong>

                                        <p>
                                            Try changing
                                            the filter
                                            or search
                                            term.
                                        </p>

                                    </div>

                                ) : (

                                    displayedIssues.map(
                                        (
                                            issue,
                                            index
                                        ) => (

                                            <div
                                                className="issue premium-issue clickable"
                                                key={`${issue.file}-${issue.line}-${index}`}
                                                onClick={() =>
                                                    viewSource(
                                                        issue
                                                    )
                                                }
                                            >

                                                <div
                                                    className={`issue-severity severity-${issue.severity?.toLowerCase()}`}
                                                >
                                                    {
                                                        issue.severity
                                                    }
                                                </div>


                                                <div className="issue-content">

                                                    <div className="issue-title-row">

                                                        <strong>
                                                            {
                                                                issue.type
                                                            }
                                                        </strong>

                                                        <span className="issue-arrow">
                                                            →
                                                        </span>

                                                    </div>


                                                    <p>
                                                        {
                                                            issue.message
                                                        }
                                                    </p>


                                                    <div className="issue-location">

                                                        <span>
                                                            {
                                                                issue.file
                                                            }
                                                        </span>

                                                        {issue.function && (
                                                            <>
                                                                <span>
                                                                    →
                                                                </span>

                                                                <span>
                                                                    {
                                                                        issue.function
                                                                    }
                                                                </span>
                                                            </>
                                                        )}

                                                        {issue.line && (
                                                            <>
                                                                <span>
                                                                    →
                                                                </span>

                                                                <span>
                                                                    Line{" "}
                                                                    {
                                                                        issue.line
                                                                    }
                                                                </span>
                                                            </>
                                                        )}

                                                        {issue.language && (
                                                            <>
                                                                <span>
                                                                    →
                                                                </span>

                                                                <span>
                                                                    {
                                                                        issue.language
                                                                    }
                                                                </span>
                                                            </>
                                                        )}

                                                    </div>

                                                </div>

                                            </div>

                                        )
                                    )

                                )}

                            </div>


                            {/* =================================================
                                LOAD ALL
                            ================================================= */}

                            {filteredIssues.length >
                                10 && (

                                <div className="issues-load-more">

                                    {!showAllIssues ? (

                                        <button
                                            className="load-all-button"
                                            onClick={() =>
                                                setShowAllIssues(
                                                    true
                                                )
                                            }
                                        >
                                            Load All Issues
                                            <span>
                                                →
                                            </span>
                                        </button>

                                    ) : (

                                        <button
                                            className="load-all-button"
                                            onClick={() =>
                                                setShowAllIssues(
                                                    false
                                                )
                                            }
                                        >
                                            Show Less
                                            <span>
                                                ↑
                                            </span>
                                        </button>

                                    )}

                                </div>

                            )}

                        </section>

                    </section>

                )}


                {/* =====================================================
                    ANALYSIS HISTORY
                ===================================================== */}

                <section className="panel history-panel">

                    <div className="history-header">

                        <div>

                            <p className="card-label">
                                ANALYSIS HISTORY
                            </p>

                            <h3>
                                Previous Analyses
                            </h3>

                            <p className="panel-subtitle">
                                Previously analyzed
                                projects
                            </p>

                        </div>


                        <button
                            className="history-refresh"
                            onClick={
                                loadHistory
                            }
                            disabled={
                                historyLoading
                            }
                        >
                            {historyLoading
                                ? "Refreshing..."
                                : "Refresh"}
                        </button>

                    </div>


                    <div className="history-list">

                        {history.length ===
                        0 ? (

                            <p className="empty">
                                No previous
                                analyses found.
                            </p>

                        ) : (

                            history.map(
                                (
                                    analysis,
                                    index
                                ) => (

                                    <div
                                        className="history-item"
                                        key={
                                            analysis.id ||
                                            analysis._id ||
                                            index
                                        }
                                    >

                                        <div className="history-project">

                                            <strong>
                                                {
                                                    analysis.project_name ||
                                                    analysis.project ||
                                                    analysis.name ||
                                                    "Unknown Project"
                                                }
                                            </strong>

                                            <span className="history-date">
                                                {
                                                    formatDate(
                                                        analysis.created_at ||
                                                        analysis.analyzed_at
                                                    )
                                                }
                                            </span>

                                        </div>


                                        <div className="history-health">

                                            <span className="history-health-label">
                                                Health
                                            </span>

                                            <span className="history-health-value">
                                                {
                                                    analysis.health_score ??
                                                    analysis
                                                        .health
                                                        ?.score ??
                                                    0
                                                }
                                                /100
                                            </span>

                                        </div>


                                        <div className="history-stat">

                                            <span className="history-stat-label">
                                                Files
                                            </span>

                                            <span className="history-stat-value">
                                                {
                                                    analysis.total_files ??
                                                    analysis
                                                        .summary
                                                        ?.total_files ??
                                                    0
                                                }
                                            </span>

                                        </div>


                                        <div className="history-stat">

                                            <span className="history-stat-label">
                                                Issues
                                            </span>

                                            <span className="history-stat-value">
                                                {
                                                    analysis.total_issues ??
                                                    analysis.issues_count ??
                                                    analysis.total_smells ??
                                                    0
                                                }
                                            </span>

                                        </div>


                                        <button
                                            className="history-view"
                                            onClick={() =>
                                                viewHistoricalAnalysis(
                                                    analysis
                                                )
                                            }
                                        >
                                            View
                                        </button>

                                    </div>

                                )
                            )

                        )}

                    </div>

                </section>


                {/* =====================================================
                    HISTORICAL DETAILS
                ===================================================== */}

                {selectedAnalysis &&
                    typeof selectedAnalysis ===
                        "object" && (

                        <section
                            id="historical-details"
                            className="panel historical-details"
                        >

                            <div className="details-header">

                                <div>

                                    <p className="card-label">
                                        HISTORICAL ANALYSIS
                                    </p>

                                    <h3>
                                        {
                                            selectedAnalysis.project_name ||
                                            selectedAnalysis.project ||
                                            selectedAnalysis.name ||
                                            "Analysis"
                                        }
                                    </h3>

                                </div>


                                <button
                                    className="close-button"
                                    onClick={() =>
                                        setSelectedAnalysis(
                                            null
                                        )
                                    }
                                >
                                    ×
                                </button>

                            </div>


                            <div className="details-grid">

                                <Detail
                                    label="Health Score"
                                    value={`${selectedAnalysis.health_score ??
                                        selectedAnalysis
                                            .health
                                            ?.score ??
                                        0}/100`}
                                />

                                <Detail
                                    label="Rating"
                                    value={
                                        selectedAnalysis.health_rating ??
                                        selectedAnalysis
                                            .health
                                            ?.rating ??
                                        "UNKNOWN"
                                    }
                                />

                                <Detail
                                    label="Files"
                                    value={
                                        selectedAnalysis.total_files ??
                                        selectedAnalysis
                                            .summary
                                            ?.total_files ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Lines"
                                    value={
                                        selectedAnalysis.total_lines ??
                                        selectedAnalysis
                                            .summary
                                            ?.total_lines ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Functions"
                                    value={
                                        selectedAnalysis.total_functions ??
                                        selectedAnalysis
                                            .summary
                                            ?.total_functions ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Classes"
                                    value={
                                        selectedAnalysis.total_classes ??
                                        selectedAnalysis
                                            .summary
                                            ?.total_classes ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Code Smells"
                                    value={
                                        selectedAnalysis.total_smells ??
                                        0
                                    }
                                />

                                <Detail
                                    label="TODOs"
                                    value={
                                        selectedAnalysis.total_todos ??
                                        0
                                    }
                                />

                                <Detail
                                    label="High Issues"
                                    value={
                                        selectedAnalysis.high_issues ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Medium Issues"
                                    value={
                                        selectedAnalysis.medium_issues ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Low Issues"
                                    value={
                                        selectedAnalysis.low_issues ??
                                        0
                                    }
                                />

                                <Detail
                                    label="Analyzed At"
                                    value={formatDate(
                                        selectedAnalysis.created_at ||
                                        selectedAnalysis.analyzed_at
                                    )}
                                />

                            </div>

                        </section>

                    )}

            </main>


            {/* =========================================================
                SOURCE INSPECTOR OVERLAY
            ========================================================= */}

            {(selectedFunction ||
                selectedIssue) && (

                <div
                    className="inspector-overlay"
                    onClick={(e) => {
                        if (
                            e.target ===
                            e.currentTarget
                        ) {
                            closeInspector();
                        }
                    }}
                >

                    <aside
                        className="source-inspector"
                        role="dialog"
                        aria-modal="true"
                        aria-label={
                            selectedFunction
                                ? "Function source inspector"
                                : "Issue source inspector"
                        }
                    >

                        {/* =================================================
                            INSPECTOR HEADER
                        ================================================= */}

                        <div className="inspector-header">

                            <div>

                                <p className="card-label">

                                    {selectedFunction
                                        ? "FUNCTION INSPECTOR"
                                        : "ISSUE INSPECTOR"}

                                </p>

                                <h2>

                                    {selectedFunction
                                        ? `${selectedFunction.name}()`
                                        : selectedIssue?.type ||
                                          "Issue"}

                                </h2>

                                <p className="inspector-file">

                                    {selectedFunction?.file ||
                                        selectedIssue?.file ||
                                        "Source"}

                                </p>

                            </div>


                            <button
                                className="close-button"
                                onClick={
                                    closeInspector
                                }
                            >
                                ×
                            </button>

                        </div>


                        {/* =================================================
                            INSPECTOR DETAILS
                        ================================================= */}

                        {selectedFunction && (

                            <div className="details-grid">

                                <Detail
                                    label="File"
                                    value={
                                        selectedFunction.file
                                    }
                                />

                                <Detail
                                    label="Line"
                                    value={
                                        selectedFunction.line
                                    }
                                />

                                <Detail
                                    label="Complexity"
                                    value={
                                        selectedFunction.complexity
                                    }
                                />

                                <Detail
                                    label="Complexity Level"
                                    value={
                                        selectedFunction.level
                                    }
                                />

                                <Detail
                                    label="Code Smells"
                                    value={
                                        selectedFunction.smells ??
                                        0
                                    }
                                />

                            </div>

                        )}


                        {/* =================================================
                            ISSUE DETAILS
                        ================================================= */}

                        {selectedIssue && (

                            <div className="details-grid">

                                <Detail
                                    label="Severity"
                                    value={
                                        selectedIssue.severity ||
                                        "UNKNOWN"
                                    }
                                />

                                <Detail
                                    label="Issue Type"
                                    value={
                                        selectedIssue.type ||
                                        "UNKNOWN"
                                    }
                                />

                                <Detail
                                    label="File"
                                    value={
                                        selectedIssue.file ||
                                        "Unknown"
                                    }
                                />

                                <Detail
                                    label="Line"
                                    value={
                                        selectedIssue.line ??
                                        "Unknown"
                                    }
                                />

                                {selectedIssue.function && (
                                    <Detail
                                        label="Function"
                                        value={
                                            selectedIssue.function
                                        }
                                    />
                                )}

                                {selectedIssue.language && (
                                    <Detail
                                        label="Language"
                                        value={
                                            selectedIssue.language
                                        }
                                    />
                                )}

                            </div>

                        )}


                        {/* =================================================
                            ISSUE MESSAGE
                        ================================================= */}

                        {selectedIssue?.message && (

                            <div className="issue-inspector-message">

                                <span>
                                    Message
                                </span>

                                <p>
                                    {
                                        selectedIssue.message
                                    }
                                </p>

                            </div>

                        )}


                        {/* =================================================
                            SOURCE CODE
                        ================================================= */}

                        <div className="source-section">

                            <div className="source-header">

                                <div>

                                    <h3>
                                        Source Code
                                    </h3>

                                    {source && (
                                        <p>
                                            Lines{" "}
                                            {
                                                source.start_line ??
                                                "?"
                                            }
                                            {" – "}
                                            {
                                                source.end_line ??
                                                "?"
                                            }
                                        </p>
                                    )}

                                </div>

                                {sourceLoading && (
                                    <span className="source-loading">
                                        Loading...
                                    </span>
                                )}

                            </div>


                            {sourceError && (
                                <div className="error">
                                    {sourceError}
                                </div>
                            )}


                            {sourceLoading && (

                                <div className="source-empty">
                                    <div className="source-loader" />
                                    Loading source
                                    code...
                                </div>

                            )}


                            {!sourceLoading &&
                                !sourceError &&
                                source && (

                                    <div className="code-editor">

                                        <div className="code-editor-top">

                                            <div className="code-file-info">

                                                <span className="code-file-icon">
                                                    {getLanguageShortCode(
                                                        selectedIssue?.language ||
                                                        selectedFunction?.language ||
                                                        "Python"
                                                    )}
                                                </span>

                                                <div>

                                                    <strong>
                                                        {
                                                            selectedFunction?.name
                                                                ? `${selectedFunction.name}()`
                                                                : selectedIssue?.type ||
                                                                  "Source"
                                                        }
                                                    </strong>

                                                    <span>
                                                        {
                                                            selectedIssue?.file ||
                                                            selectedFunction?.file ||
                                                            "Source file"
                                                        }
                                                    </span>

                                                </div>

                                            </div>


                                            <div className="code-location">

                                                {
                                                    source.start_line
                                                }

                                                {" – "}

                                                {
                                                    source.end_line
                                                }

                                            </div>

                                        </div>


                                        <div className="code-viewer">
    {sourceLines.length === 0 ? (
        <div className="source-empty">
            Source code was not returned by the analyzer.
        </div>
    ) : (
        sourceLines.map((sourceLine, index) => (
            <div
                className={`code-line ${
                    sourceLine.is_target
                        ? "target-line"
                        : ""
                }`}
                key={`${sourceLine.line}-${index}`}
            >
                <span className="line-number">
                    {sourceLine.line}
                </span>

                <span className="line-indicator">
                    {sourceLine.is_target
                        ? "›"
                        : ""}
                </span>

                <code>
                    {sourceLine.code || " "}
                </code>
            </div>
        ))
    )}
</div>

                                    </div>

                                )}

                        </div>


                        {/* =================================================
                            AI ACTIONS
                        ================================================= */}

                        {selectedIssue &&
                            source && (

                                <div className="ai-section">

                                    <div className="ai-actions">

                                        <button
                                            className="ai-button"
                                            onClick={
                                                explainIssueWithAI
                                            }
                                            disabled={
                                                aiLoading ||
                                                !selectedIssue ||
                                                !source
                                            }
                                        >
                                            {aiLoading
                                                ? "Analyzing with AI..."
                                                : "Explain with AI"}
                                        </button>


                                        <button
                                            className="ai-button"
                                            onClick={
                                                suggestFixWithAI
                                            }
                                            disabled={
                                                aiFixLoading ||
                                                !selectedIssue ||
                                                !source
                                            }
                                        >
                                            {aiFixLoading
                                                ? "Generating Fix..."
                                                : "Suggest Fix with AI"}
                                        </button>

                                    </div>


                                    {aiError && (
                                        <div className="ai-error">
                                            {
                                                aiError
                                            }
                                        </div>
                                    )}


                                    {aiExplanation && (

                                        <div className="ai-explanation">

                                            <div className="ai-result-header">
                                                <span>
                                                    AI
                                                </span>

                                                <h3>
                                                    AI Explanation
                                                </h3>
                                            </div>

                                            <pre>
                                                {
                                                    aiExplanation
                                                }
                                            </pre>

                                        </div>

                                    )}


                                    {aiFixError && (
                                        <div className="ai-error">
                                            {
                                                aiFixError
                                            }
                                        </div>
                                    )}


                                    {aiFix && (

                                        <div className="ai-explanation">

                                            <div className="ai-result-header">
                                                <span>
                                                    AI
                                                </span>

                                                <h3>
                                                    AI Suggested Fix
                                                </h3>
                                            </div>

                                            <pre>
                                                {
                                                    aiFix
                                                }
                                            </pre>

                                        </div>

                                    )}

                                </div>

                            )}

                    </aside>

                </div>

            )}

        </div>
    );
}


// =============================================================
// LANGUAGE HELPERS
// =============================================================

const LANGUAGE_KEYS = {
    Python: new Set(["python", "py"]),
    Java: new Set(["java"]),
    JavaScript: new Set(["javascript", "js", "nodejs", "node"]),
    TypeScript: new Set(["typescript", "ts"]),
};

function normalizeLanguageKey(value) {
    return String(value || "")
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "");
}

function isMatchingLanguage(value, language) {
    const normalized = normalizeLanguageKey(value);
    if (!normalized) return false;

    for (const alias of LANGUAGE_KEYS[language] || []) {
        if (normalized === alias) return true;
    }

    return normalized === normalizeLanguageKey(language);
}

function findLanguageData(payload, language, depth = 0) {
    if (!payload || depth > 6) return null;

    if (Array.isArray(payload)) {
        for (const item of payload) {
            if (!item || typeof item !== "object") continue;

            if (
                isMatchingLanguage(
                    item.language ||
                        item.language_name ||
                        item.name ||
                        item.lang,
                    language
                )
            ) {
                return item;
            }

            const nested = findLanguageData(
                item,
                language,
                depth + 1
            );
            if (nested) return nested;
        }
        return null;
    }

    if (typeof payload !== "object") return null;

    for (const [key, value] of Object.entries(payload)) {
        if (isMatchingLanguage(key, language)) {
            if (value && typeof value === "object") {
                return value;
            }
        }
    }

    for (const value of Object.values(payload)) {
        if (!value || typeof value !== "object") continue;
        const nested = findLanguageData(
            value,
            language,
            depth + 1
        );
        if (nested) return nested;
    }

    return null;
}

    function buildLanguageIssueFallback(issues, language) {
        if (!Array.isArray(issues)) return null;

        const languageIssues = issues.filter((issue) =>
            isMatchingLanguage(
                issue?.language,
                language
            )
        );

        if (languageIssues.length === 0) return null;

        const files = new Set(
            languageIssues
                .map((issue) => issue?.file)
                .filter(Boolean)
        );

        return {
            files: files.size,
            lines: 0,
            functions: new Set(
                languageIssues
                    .map((issue) => issue?.function)
                    .filter(Boolean)
            ).size,
            issues: languageIssues.length,
        };
    }


// =============================================================
// METRIC
// =============================================================

function Metric({
    label,
    value,
}) {
    return (
        <div className="metric premium-metric">

            <div className="metric-top">

                <span className="metric-label">
                    {label}
                </span>

                <span className="metric-dot" />

            </div>

            <strong className="metric-value">
                {value}
            </strong>

            <div className="metric-footer">
                Analysis metric
            </div>

        </div>
    );
}


// =============================================================
// DETAIL
// =============================================================

function Detail({
    label,
    value,
}) {
    return (
        <div className="detail-item">

            <span>
                {label}
            </span>

            <strong
                title={
                    value !== undefined &&
                    value !== null
                        ? String(value)
                        : ""
                }
            >
                {value ??
                    "Unknown"}
            </strong>

        </div>
    );
}


// =============================================================
// LANGUAGE CARD
// =============================================================

function LanguageCard({
    language,
    data,
}) {
    if (!data) {
        return (
            <div className="language-card language-disabled">
                <div className="language-card-header">
                    <div className="language-icon">
                        {getLanguageShortCode(language)}
                    </div>
                    <div>
                        <strong>{language}</strong>
                        <span>Not detected</span>
                    </div>
                </div>
                <div className="language-empty">
                    No language-specific data returned
                </div>
            </div>
        );
    }

    const score =
        data.health_score ??
        data.score ??
        data.health?.score ??
        null;

    const files =
        data.files ??
        data.total_files ??
        data.file_count ??
        0;

    const lines =
        data.lines ??
        data.total_lines ??
        data.line_count ??
        0;

    const functions =
        data.functions ??
        data.total_functions ??
        data.function_count ??
        0;

    const issues =
        data.issues ??
        data.total_issues ??
        data.issues_count ??
        0;

    const rating =
        data.health_rating ??
        data.health?.rating ??
        data.rating ??
        null;

    return (
        <div className="language-card">
            <div className="language-card-header">
                <div className="language-icon">
                    {getLanguageShortCode(language)}
                </div>
                <div className="language-title">
                    <strong>{language}</strong>
                    <span>{rating || "Language analysis"}</span>
                </div>
                {score !== null && (
                    <div className="language-health-pill">
                        {score}/100
                    </div>
                )}
            </div>

            <div className="language-score">
                <span>Health</span>
                <strong>
                    {score ?? "—"}
                    {score !== null && <small>/100</small>}
                </strong>
            </div>

            <div className="language-metrics">
                <div>
                    <span>Files</span>
                    <strong>{files}</strong>
                </div>
                <div>
                    <span>Lines</span>
                    <strong>{lines}</strong>
                </div>
                <div>
                    <span>Functions</span>
                    <strong>{functions}</strong>
                </div>
                <div>
                    <span>Issues</span>
                    <strong>{issues}</strong>
                </div>
            </div>
        </div>
    );
}


// =============================================================
// LANGUAGE SHORT CODE
// =============================================================

function getLanguageShortCode(
    language
) {
    const value =
        String(
            language || ""
        ).toLowerCase();

    if (
        value.includes("typescript") ||
        value === "ts"
    ) {
        return "TS";
    }

    if (
        value.includes("javascript") ||
        value === "js"
    ) {
        return "JS";
    }

    if (
        value.includes("java") &&
        !value.includes("script")
    ) {
        return "JV";
    }

    return "PY";
}


export default App;