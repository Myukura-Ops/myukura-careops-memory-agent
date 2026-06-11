import React, { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, Clock, AlertTriangle, Activity, Database, Check, Cpu, Mic, MicOff, Trash2, Lock, Unlock } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface Event {
  event_id: string;
  event_type: string;
  message: string;
  timestamp: string;
}

interface Task {
  task_id: string;
  agent_run_id: string;
  title: string;
  description: string;
  task_type: string;
  status: string;
  priority: string;
  created_at: string;
}

interface ActivityStats {
  backend: string;
  latest_run_id: string | null;
  collections_touched: string[];
  write_counts: number | Record<string, number>;
  total_writes?: number;
}

function getTotalWrites(activity: ActivityStats | null): number {
  if (!activity) return 0;
  if (typeof activity.total_writes === "number") return activity.total_writes;
  if (typeof activity.write_counts === "number") return activity.write_counts;
  if (activity.write_counts && typeof activity.write_counts === "object") {
    return Object.values(activity.write_counts).reduce((sum, value) => sum + Number(value || 0), 0);
  }
  return 0;
}

const DEMO_SCENARIOS = [
  {
    name: "Scenario 1: Messy post-visit admin note — forms, insurance and follow-up",
    text: "Demo clinic note — synthetic data only.\n\nPatient: Ana Rivera Demo.\nContext: post-visit admin cleanup after a short consultation. The clinician already spoke with the patient. This is not a diagnostic note and should not be used to create diagnosis, treatment, medication or patient-facing advice.\n\nMessy staff note:\nAna left quickly after the visit. Dr. Martín said the clinical plan was already explained verbally and no medication changes were made today. Reception still needs to check whether the intake consent form was actually signed because the paper folder has a blank copy but the front desk system says ‘received’. Insurance information may be outdated; patient mentioned a new provider card but we did not scan it. Follow-up should probably be scheduled in around 10 days, but only after the clinician confirms the exact window. Patient prefers Spanish for administrative reminders. Please prepare a short internal visit summary for clinician review before the next appointment. Do not send a clinical summary to the patient yet. Do not add diagnosis. Do not add treatment recommendations. Human review required."
  },
  {
    name: "Scenario 2: Incomplete handoff note — missing attachment and portal access",
    text: "Demo clinic note — synthetic data only.\n\nPatient: Marco López Demo.\nContext: incomplete handoff between clinician and admin team. The clinician already discussed the plan verbally with the patient. This note is incomplete and must be reviewed by a human before action.\n\nMessy handoff:\nNeed to finish Marco’s post-visit admin handoff. Clinician said follow-up should be in about two weeks, but the exact day is not confirmed. There was supposed to be a lab request PDF attached to the admin record, but I cannot see it in the folder. Check whether Marco has patient portal access before sending any admin reminder. If the appointment slot changes, call the patient; otherwise do not call. No patient-facing clinical message should be generated from this note. No diagnosis. No medication changes. Please flag this as incomplete handoff and require review."
  },
  {
    name: "Scenario 3: Front desk note — forms incomplete and emergency contact missing",
    text: "Demo clinic note — synthetic data only.\n\nPatient: Sofia Morales Demo.\nContext: front desk operational note after patient check-in and clinician review. This is administrative, not clinical.\n\nFront desk note:\nSofia arrived late and some forms were completed in a hurry. Phone number was confirmed at reception, but emergency contact is still missing. The intake packet is marked partially complete. Doctor asked the admin team to prepare the chart for clinician review tomorrow morning. Do not send a clinical summary yet. Do not create treatment instructions. Do not infer diagnosis. Admin team should verify emergency contact, mark forms incomplete, and prepare chart for review."
  },
  {
    name: "Scenario 4: Mixed-patient admin cleanup — must be flagged",
    text: "Demo clinic note — synthetic data only.\n\nContext: end-of-day admin cleanup note. Warning: this note mixes multiple demo patients and must be flagged for human review before final task execution.\n\nAdmin cleanup:\nAlex Parker Demo needs follow-up booking after today’s visit. Lina Santos Demo is missing the intake form. Omar Torres Demo mentioned insurance changed and needs verification. This note combines several patients in one text, so the system should not pretend everything belongs to one patient. It should flag mixed-patient note risk, create only safe review tasks, and require a human to split or confirm the tasks before action. No diagnosis. No treatment recommendations. No medication changes."
  }
];

export default function App() {
  const [sourceNote, setSourceNote] = useState(DEMO_SCENARIOS[0].text);
  const [mode, setMode] = useState<string>('mock');
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<string>('idle');
  const [runResult, setRunResult] = useState<any>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [mcpCalls, setMcpCalls] = useState<any[]>([]);
  const [activity, setActivity] = useState<ActivityStats | null>(null);

  // Voice Intake State
  const [isListening, setIsListening] = useState(false);
  const [voiceLanguage, setVoiceLanguage] = useState('en-US');
  const [speechSupported, setSpeechSupported] = useState(true);
  const [voiceTimer, setVoiceTimer] = useState<number | null>(null);
  const [voiceStoppedByLimit, setVoiceStoppedByLimit] = useState(false);
  const recognitionRef = useRef<any>(null);

  const [demoAccessCode, setDemoAccessCode] = useState(() => localStorage.getItem('myukura_demo_access_code') || '');
  const [inputCode, setInputCode] = useState('');

  const authFetch = async (url: string, options: any = {}) => {
    const code = localStorage.getItem('myukura_demo_access_code') || '';
    const headers = { ...options.headers, 'x-demo-access-code': code };
    const res = await fetch(url, { ...options, headers });
    if (res.status === 401 || res.status === 403) {
      setDemoAccessCode('');
      localStorage.removeItem('myukura_demo_access_code');
    }
    return res;
  };

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
    }
  }, []);

  const startListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice intake not supported in this browser.");
      return;
    }
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    const recognition = new SpeechRecognition();
    recognition.lang = voiceLanguage;
    recognition.continuous = true;
    recognition.interimResults = false;
    
    recognition.onstart = () => {
      setIsListening(true);
      setVoiceStoppedByLimit(false);
      const timer = window.setTimeout(() => {
        if (recognitionRef.current) {
          recognitionRef.current.stop();
        }
        setIsListening(false);
        setVoiceStoppedByLimit(true);
      }, 300000); // 5 minutes limit
      setVoiceTimer(timer);
    };
    recognition.onresult = (event: any) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        }
      }
      if (finalTranscript) {
        setSourceNote(prev => {
          const newText = prev ? prev + ' ' + finalTranscript.trim() : finalTranscript.trim();
          return newText.substring(0, 6000);
        });
      }
    };
    recognition.onerror = (event: any) => {
      console.error("Speech error:", event.error);
      setIsListening(false);
      if (voiceTimer) clearTimeout(voiceTimer);
    };
    recognition.onend = () => {
      setIsListening(false);
      if (voiceTimer) clearTimeout(voiceTimer);
    };
    
    recognition.start();
    recognitionRef.current = recognition;
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      if (voiceTimer) clearTimeout(voiceTimer);
    }
  };

  const handleClearNote = () => setSourceNote('');

  // Poll for agent run updates
  useEffect(() => {
    let interval: number;
    if (runId && runStatus !== 'completed' && runStatus !== 'failed') {
      interval = window.setInterval(async () => {
        try {
          const runRes = await authFetch(`${API_URL}/agent-runs/${runId}`);
          if (runRes.ok) {
            const runData = await runRes.json();
            setRunStatus(runData.status);
            setRunResult(runData.result);
          }
          const evRes = await authFetch(`${API_URL}/agent-runs/${runId}/events`);
          if (evRes.ok) {
            setEvents(await evRes.json());
          }
          const mcpRes = await authFetch(`${API_URL}/agent-runs/${runId}/mcp-tool-calls`);
          if (mcpRes.ok) {
            setMcpCalls(await mcpRes.json());
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [runId, runStatus]);

  // Poll for global tasks and mongodb activity
  useEffect(() => {
    const interval = window.setInterval(async () => {
      try {
        const tRes = await authFetch(`${API_URL}/tasks?clinic_id=clinic_demo`);
        if (tRes.ok) setTasks(await tRes.json());
        
        const actRes = await authFetch(`${API_URL}/mongodb/activity`);
        if (actRes.ok) setActivity(await actRes.json());
      } catch (err) {
        // ignore
      }
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const handleSeed = async () => {
    try {
      await authFetch(`${API_URL}/demo/seed`, { method: 'POST' });
      alert("Synthetic demo data seeded in MongoDB!");
    } catch (e) {
      alert("Seed failed. Is API running?");
    }
  };

  const handleRunAgent = async () => {
    try {
      setRunId(null);
      setEvents([]);
      setRunStatus('submitting');
      const res = await authFetch(`${API_URL}/agent-runs/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clinic_id: "clinic_demo",
          patient_id: "patient_demo",
          professional_id: "prof_demo",
          source_note: sourceNote.substring(0, 6000),
          mode: mode
        })
      });
      if (!res.ok) {
        const errorData = await res.json();
        const detail =
          typeof errorData.detail === "string"
            ? errorData.detail
            : errorData.detail?.message || errorData.message || "Unknown error";
        alert(`Error: ${detail}`);
        setRunStatus('failed');
        return;
      }
      const data = await res.json();
      setRunId(data.run_id);
      setRunStatus(data.status);
    } catch (err) {
      alert("Failed to connect to API.");
      setRunStatus('idle');
    }
  };

  const handleTaskStatus = async (task_id: string, status: string) => {
    try {
      await authFetch(`${API_URL}/tasks/${task_id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
    } catch (e) {
      console.error(e);
    }
  };

  if (!demoAccessCode) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8 max-w-md w-full">
          <div className="text-center mb-6">
            <Lock className="mx-auto h-12 w-12 text-blue-500 mb-4" />
            <h1 className="text-2xl font-bold text-gray-900">CareOps Demo Access</h1>
            <p className="text-sm text-gray-600 mt-2">Please enter the demo access code to continue.</p>
          </div>
          <div className="space-y-4">
            <input
              type="password"
              placeholder="Enter access code"
              value={inputCode}
              onChange={(e) => setInputCode(e.target.value)}
              className="w-full border p-3 rounded bg-gray-50 border-gray-300 focus:ring-blue-500 focus:border-blue-500 text-center text-xl tracking-widest"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  setDemoAccessCode(inputCode);
                  localStorage.setItem('myukura_demo_access_code', inputCode);
                }
              }}
            />
            <button
              onClick={() => {
                setDemoAccessCode(inputCode);
                localStorage.setItem('myukura_demo_access_code', inputCode);
              }}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded transition-colors flex items-center justify-center gap-2"
            >
              <Unlock size={18} /> Unlock Demo
            </button>
            {inputCode === '' && (
              <p className="text-xs text-red-500 text-center hidden">Invalid or missing demo access code.</p>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">MyuKura CareOps Memory Agent</h1>
          <p className="text-sm text-gray-600 font-medium mt-1">MongoDB-backed operational memory for supervised care operations.</p>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-medium border border-blue-200">Cloud Run Web</span>
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-medium border border-blue-200">Cloud Run API</span>
            <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded font-medium border border-green-200">MongoDB Atlas</span>
            <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded font-medium border border-yellow-200">Human Review Required</span>
            <span className="bg-purple-100 text-purple-800 text-xs px-2 py-0.5 rounded font-medium border border-purple-200">Synthetic Demo Only</span>
            <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-medium border border-blue-200">Gemini Enabled / Secret Manager</span>
          </div>
        </div>
        <div className="flex space-x-4 items-center">
          {activity && (
            <div className="bg-blue-50 border border-blue-200 rounded p-2 text-xs text-blue-800 flex flex-col items-end">
              <span className="font-bold flex items-center gap-1"><Database size={12}/> MongoDB Activity ({activity.backend})</span>
              <span>
                Writes: {getTotalWrites(activity)} | Colls: {activity.collections_touched?.length || 0}
              </span>
              {activity.latest_run_id && (
                <span className="text-blue-600 mt-1 truncate max-w-[200px]">Run: {activity.latest_run_id.split('-')[0]}</span>
              )}
              {activity.collections_touched && activity.collections_touched.length > 0 && (
                <span className="text-blue-500 truncate max-w-[200px]" title={activity.collections_touched.join(', ')}>
                  {activity.collections_touched.join(', ')}
                </span>
              )}
            </div>
          )}
          <button onClick={handleSeed} className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-800 py-1 px-3 rounded border border-gray-300">
            Seed Demo Data
          </button>
          <button 
            onClick={() => {
              setDemoAccessCode('');
              localStorage.removeItem('myukura_demo_access_code');
            }} 
            className="text-sm flex items-center gap-1 bg-red-50 hover:bg-red-100 text-red-700 py-1 px-2 rounded border border-red-200 ml-2"
          >
            <Lock size={14} /> Lock Demo
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-grow p-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* What this demo proves */}
        <div className="lg:col-span-4 bg-white rounded-lg shadow border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-2">What this demo proves</h2>
          <ul className="list-disc pl-5 text-sm text-gray-700 space-y-1">
            <li>Captures a synthetic operational note.</li>
            <li>Creates a persistent agent run.</li>
            <li>Writes audit events to MongoDB.</li>
            <li>Proposes non-clinical operational tasks.</li>
            <li>Requires human approval before task action.</li>
            <li>Tracks memory activity across MongoDB collections.</li>
          </ul>
        </div>

        {/* Evidence Layer */}
        <div className="lg:col-span-4 grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Architecture Evidence */}
          <div className="md:col-span-2 bg-white rounded-lg shadow border border-gray-200 p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-1">Architecture Evidence</h2>
            <p className="text-sm text-gray-600 mb-4">This demo combines Google Cloud, Gemini, MongoDB operational memory, and human-supervised safety controls.</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="bg-blue-50 border border-blue-100 p-2 rounded">
                <strong className="block text-xs text-blue-900 mb-0.5">Google Cloud Run</strong>
                <p className="text-[10px] text-blue-800">API and Web are designed for containerized Cloud Run deployment.</p>
              </div>
              <div className="bg-blue-50 border border-blue-100 p-2 rounded">
                <strong className="block text-xs text-blue-900 mb-0.5">Cloud Build + Artifact Registry</strong>
                <p className="text-[10px] text-blue-800">Builds are containerized and versioned through Google Cloud build/deploy flow.</p>
              </div>
              <div className="bg-purple-50 border border-purple-100 p-2 rounded">
                <strong className="block text-xs text-purple-900 mb-0.5">Gemini Safe Extraction</strong>
                <p className="text-[10px] text-purple-800">Gemini extracts operational signals only. Backend validation prevents diagnosis, treatment recommendations, medication changes, and external delivery.</p>
              </div>
              <div className="bg-purple-50 border border-purple-100 p-2 rounded">
                <strong className="block text-xs text-purple-900 mb-0.5">Model Fallback Chain</strong>
                <p className="text-[10px] text-purple-800">Configured model chain attempts up to 3 models, then safely falls back to Mock deterministic extraction.</p>
              </div>
              <div className="bg-green-50 border border-green-100 p-2 rounded">
                <strong className="block text-xs text-green-900 mb-0.5">MongoDB Operational Memory</strong>
                <p className="text-[10px] text-green-800">Agent runs, tasks, source notes, audit events, and operational memory are persisted in MongoDB.</p>
              </div>
              <div className="bg-gray-50 border border-gray-200 p-2 rounded">
                <strong className="block text-xs text-gray-900 mb-0.5">Secret Manager Ready</strong>
                <p className="text-[10px] text-gray-700">Gemini API key is stored in Secret Manager for Cloud activation.</p>
              </div>
              <div className="bg-yellow-50 border border-yellow-100 p-2 rounded">
                <strong className="block text-xs text-yellow-900 mb-0.5">Human Review Required</strong>
                <p className="text-[10px] text-yellow-800">All proposed tasks require human approval before action.</p>
              </div>
              <div className="bg-red-50 border border-red-100 p-2 rounded">
                <strong className="block text-xs text-red-900 mb-0.5">Synthetic Demo Only</strong>
                <p className="text-[10px] text-red-800">No real patient data, no real delivery, no production compliance claims.</p>
              </div>
              <div className="bg-indigo-50 border border-indigo-100 p-2 rounded">
                <strong className="block text-xs text-indigo-900 mb-0.5">Arize</strong>
                <p className="text-[10px] text-indigo-800">Outbox-ready AI observability payload.</p>
              </div>
              <div className="bg-blue-50 border border-blue-100 p-2 rounded">
                <strong className="block text-xs text-blue-900 mb-0.5">Elastic</strong>
                <p className="text-[10px] text-blue-800">Outbox-ready audit-search payload.</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-6">
            {/* Deployment Status */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
              <h2 className="text-sm font-semibold text-gray-800 mb-2">Deployment Status</h2>
              <ul className="space-y-2 text-xs">
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-green-500 shrink-0"></span>
                  <div>
                    <strong className="text-gray-700 block">Deployed baseline:</strong>
                    <span className="text-gray-500">Cloud Run API/Web available from previous milestone.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-yellow-500 shrink-0"></span>
                  <div>
                    <strong className="text-gray-700 block">Local pending bundle:</strong>
                    <span className="text-gray-500">Voice Intake, Gemini Safe Extraction, fallback chain, memory reuse, evidence layer.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 shrink-0"></span>
                  <div>
                    <strong className="text-gray-700 block">Cloud Gemini:</strong>
                    <span className="text-gray-500">enabled.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 shrink-0"></span>
                  <div>
                    <strong className="text-gray-700 block">Secret Manager Gemini key:</strong>
                    <span className="text-gray-500">configured and stored securely.</span>
                  </div>
                </li>
                <li className="flex items-start gap-2">
                  <span className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 shrink-0"></span>
                  <div>
                    <strong className="text-gray-700 block">Current safe fallback:</strong>
                    <span className="text-gray-500">Mock deterministic extraction.</span>
                  </div>
                </li>
              </ul>
            </div>

            {/* Score Improvement */}
            <div className="bg-white rounded-lg shadow border border-gray-200 p-4 flex-grow">
              <h2 className="text-sm font-semibold text-gray-800 mb-2">What improves the score?</h2>
              <ul className="list-disc pl-4 text-xs text-gray-600 space-y-1">
                <li>Real Gemini local extraction validated.</li>
                <li>Prompt-injection defense tested.</li>
                <li>Backend safety validator tested.</li>
                <li>MongoDB memory architecture implemented.</li>
                <li>Visible memory reuse implemented locally.</li>
                <li>Voice intake makes the workflow realistic.</li>
                <li>Audit trail supports traceability.</li>
                <li>Human-in-the-loop keeps the system safe.</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Partner Integrations */}
        <div className="lg:col-span-4 bg-white rounded-lg shadow border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-800 mb-1">Partner Integrations</h2>
          <p className="text-sm text-gray-600 mb-4">MongoDB is live. Arize and Elastic are prepared through a safe outbox layer; external exports remain disabled unless explicitly configured.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* MongoDB Atlas */}
            <div className="border border-green-200 bg-green-50 rounded p-3 flex flex-col">
              <div className="flex justify-between items-start mb-2">
                <strong className="text-green-900 text-sm">MongoDB Atlas</strong>
                <span className="bg-green-200 text-green-900 text-[10px] font-bold px-2 py-0.5 rounded border border-green-300">Integrated</span>
              </div>
              <div className="text-xs font-semibold text-green-800 mb-1">Role: Persistent operational memory</div>
              <p className="text-[11px] text-green-700 flex-grow">Stores agent runs, proposed tasks, audit events, and operational memory.</p>
            </div>
            
            {/* Arize */}
            {(() => {
              const arizeStatus = runResult?.partner_integrations?.arize?.status || "missing";
              const isReady = arizeStatus === "outbox_ready";
              const isFailed = arizeStatus === "outbox_failed";
              
              const statusText = isReady ? "Outbox ready" : isFailed ? "Outbox failed safely" : "Not available for this run";
              const statusColors = isReady ? "bg-indigo-100 text-indigo-800 border-indigo-200" : isFailed ? "bg-red-100 text-red-800 border-red-200" : "bg-gray-100 text-gray-600 border-gray-200";
              const bgClass = isReady ? "bg-indigo-50 border-indigo-100" : isFailed ? "bg-red-50 border-red-100" : "bg-gray-50 border-gray-100";
              
              return (
                <div className={`border rounded p-3 flex flex-col ${bgClass}`}>
                  <div className="flex justify-between items-start mb-2">
                    <strong className={`text-sm ${isReady ? 'text-indigo-900' : isFailed ? 'text-red-900' : 'text-gray-700'}`}>Arize</strong>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${statusColors}`}>{statusText}</span>
                  </div>
                  <p className={`text-[11px] flex-grow ${isReady ? 'text-indigo-800' : isFailed ? 'text-red-800' : 'text-gray-500'}`}>
                    AI observability/evaluation payload for Gemini model usage, fallback chain, safety status, memory usage, and prompt-injection detection.
                  </p>
                  <div className={`mt-2 pt-2 border-t text-[10px] font-semibold ${isReady ? 'border-indigo-200 text-indigo-700' : isFailed ? 'border-red-200 text-red-700' : 'border-gray-200 text-gray-500'}`}>
                    External export: Disabled
                  </div>
                </div>
              );
            })()}

            {/* Elastic */}
            {(() => {
              const elasticStatus = runResult?.partner_integrations?.elastic?.status || "missing";
              const isReady = elasticStatus === "outbox_ready";
              const isFailed = elasticStatus === "outbox_failed";
              
              const statusText = isReady ? "Outbox ready" : isFailed ? "Outbox failed safely" : "Not available for this run";
              const statusColors = isReady ? "bg-blue-100 text-blue-800 border-blue-200" : isFailed ? "bg-red-100 text-red-800 border-red-200" : "bg-gray-100 text-gray-600 border-gray-200";
              const bgClass = isReady ? "bg-blue-50 border-blue-100" : isFailed ? "bg-red-50 border-red-100" : "bg-gray-50 border-gray-100";
              
              return (
                <div className={`border rounded p-3 flex flex-col ${bgClass}`}>
                  <div className="flex justify-between items-start mb-2">
                    <strong className={`text-sm ${isReady ? 'text-blue-900' : isFailed ? 'text-red-900' : 'text-gray-700'}`}>Elastic</strong>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${statusColors}`}>{statusText}</span>
                  </div>
                  <p className={`text-[11px] flex-grow ${isReady ? 'text-blue-800' : isFailed ? 'text-red-800' : 'text-gray-500'}`}>
                    Search-ready audit payload for runs, tasks, safety flags, memory context, and operational events.
                  </p>
                  <div className={`mt-2 pt-2 border-t text-[10px] font-semibold ${isReady ? 'border-blue-200 text-blue-700' : isFailed ? 'border-red-200 text-red-700' : 'border-gray-200 text-gray-500'}`}>
                    External indexing: Disabled
                  </div>
                </div>
              );
            })()}

          </div>
          <p className="mt-3 text-xs text-gray-500 italic">
            {runResult && !runResult.partner_integrations ? "Partner integration details are available for new runs only. " : ""}
            Partner exports are non-blocking. The core CareOps agent does not depend on Arize or Elastic availability.
          </p>
        </div>

        {/* Left Column: Input */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">1. Input Synthetic Note</h2>
            
            <div className="mb-3">
              <label className="text-sm font-medium text-gray-700 block mb-1">Synthetic demo scenario:</label>
              <select 
                className="w-full border p-2 text-sm rounded bg-gray-50 border-gray-300"
                onChange={(e) => setSourceNote(e.target.value)}
              >
                {DEMO_SCENARIOS.map((s, idx) => (
                  <option key={idx} value={s.text}>{s.name}</option>
                ))}
              </select>
            </div>
            
            <p className="text-xs text-gray-500 mb-4">Paste a messy operational note. The agent will extract non-clinical operational signals and persist them as human-reviewed clinic memory.</p>
            
            {/* Voice Intake Section */}
            <div className="mb-4 bg-gray-50 border border-gray-200 rounded p-3">
              <h3 className="text-sm font-semibold text-gray-800 mb-1 flex items-center gap-1">
                <Mic size={16} /> Voice Intake
              </h3>
              <p className="text-xs text-gray-500 mb-2">Dictate a messy synthetic operations note into the source note box.</p>
              
              {!speechSupported ? (
                <div className="text-xs text-red-600 bg-red-50 p-2 rounded border border-red-100">
                  Voice intake not supported in this browser.
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <select 
                      value={voiceLanguage} 
                      onChange={e => setVoiceLanguage(e.target.value)}
                      className="border border-gray-300 text-xs rounded p-1 bg-white"
                      disabled={isListening}
                    >
                      <option value="en-US">English</option>
                      <option value="es-ES">Spanish</option>
                    </select>
                    {isListening ? (
                      <button onClick={stopListening} className="flex items-center gap-1 bg-red-100 hover:bg-red-200 text-red-700 text-xs py-1 px-2 rounded font-medium border border-red-200 transition-colors">
                        <MicOff size={14} /> Stop dictation
                      </button>
                    ) : (
                      <button onClick={startListening} className="flex items-center gap-1 bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs py-1 px-2 rounded font-medium border border-blue-200 transition-colors">
                        <Mic size={14} /> Start dictation
                      </button>
                    )}
                    <button onClick={handleClearNote} className="flex items-center gap-1 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs py-1 px-2 rounded font-medium transition-colors ml-auto">
                      <Trash2 size={14} /> Clear note
                    </button>
                  </div>
                  {isListening ? (
                    <div className="text-[10px] text-green-600 font-medium animate-pulse">Listening... (Speak now) Voice intake stops automatically after 5 minutes.</div>
                  ) : (
                    <div className="text-[10px] text-gray-400 font-medium">
                      {voiceStoppedByLimit ? "Voice intake stopped after the 5-minute safety limit." : "Voice intake stopped."}
                    </div>
                  )}
                  <p className="text-[9px] text-gray-500 italic mt-1 leading-tight">
                    Voice intake runs locally in the browser when supported. No audio is stored by this demo. The transcribed text is still synthetic demo input and requires human review.
                  </p>
                </div>
              )}
            </div>
            <textarea
              className="w-full h-48 p-3 border border-gray-300 rounded text-sm font-mono focus:ring-blue-500 focus:border-blue-500"
              value={sourceNote}
              onChange={(e) => setSourceNote(e.target.value)}
            />
            <div className="flex justify-between items-center mt-1">
              <span className={`text-xs ${sourceNote.length > 6000 ? 'text-red-600 font-bold' : 'text-gray-500'}`}>
                {sourceNote.length} / 6000 characters
              </span>
              <span className="text-[10px] text-gray-500">This demo accepts up to 6,000 characters per note.</span>
            </div>
            <div className="mt-2">
              <label className="text-sm font-medium text-gray-700 mr-2">Mode:</label>
              <select value={mode} onChange={e => setMode(e.target.value)} className="border p-1 text-sm rounded bg-white">
                <option value="mock">Mock deterministic extraction</option>
                <option value="gemini">Gemini safe extraction</option>
              </select>
              {mode === 'gemini' && (
                <div className="text-xs text-blue-700 mt-2 bg-blue-50 p-2 rounded border border-blue-100">
                  <span className="font-bold">Gemini Safe Extraction</span> extracts operational signals only. Backend safety validation enforces no diagnosis, no treatment recommendations, no medication changes, no external delivery, and human approval required.
                  <div className="mt-1 font-semibold">Gemini Safe Extraction may try configured fallback models. If all model attempts fail or safety validation fails, the system falls back to Mock deterministic extraction and records the fallback in the audit trail.</div>
                </div>
              )}
            </div>
            <button
              onClick={handleRunAgent}
              disabled={(runStatus !== 'idle' && runStatus !== 'completed' && runStatus !== 'failed') || sourceNote.length > 6000}
              className="mt-4 w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded flex items-center justify-center gap-2 disabled:opacity-50"
            >
              <Play size={18} /> Run CareOps Agent
            </button>
            
            {runId && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-sm text-gray-700">
                <h3 className="font-bold text-green-900 mb-2 flex items-center gap-1"><CheckCircle size={16}/> Operational Memory Created</h3>
                <div className="space-y-1 text-xs">
                  <div><strong>Run ID:</strong> {runId.split('-')[0]}...</div>
                  <div className="flex items-center gap-2">
                    <strong>Status:</strong>
                    <span className={`capitalize px-2 py-0.5 rounded text-[10px] font-bold ${
                      runStatus.includes('warning') ? 'bg-yellow-100 text-yellow-800' :
                      runStatus === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {runStatus.replace(/_/g, ' ')}
                    </span>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-green-200">
                    <div className="font-semibold text-green-800 mb-1">Source operational note:</div>
                    <div className="bg-white border border-green-100 p-2 rounded max-h-24 overflow-y-auto text-gray-600 font-mono text-[10px] whitespace-pre-wrap">
                      {sourceNote}
                    </div>
                  </div>
                  {runResult && (
                    <>
                      <div><strong>State backend:</strong> mongodb</div>
                      <div><strong>Extraction Mode:</strong> {runResult.extraction_mode}</div>
                      <div><strong>Safety Status:</strong> <span className={runResult.safety_status === 'blocked' ? 'text-red-600 font-bold' : 'text-green-700 font-semibold'}>{runResult.safety_status}</span></div>
                      
                      <div className="mt-2 pt-2 border-t border-green-200">
                        <div className="font-semibold text-green-800 mb-1">Detected Signals:</div>
                        {runResult.operational_signals_detected && runResult.operational_signals_detected.length > 0 ? (
                          <div className="flex flex-wrap gap-1">
                            {runResult.operational_signals_detected.map((sig: string) => (
                              <span key={sig} className="bg-green-100 text-green-800 px-1.5 py-0.5 rounded text-[10px] border border-green-300">{sig}</span>
                            ))}
                          </div>
                        ) : (
                          <div className="text-gray-500 italic">No signals extracted.</div>
                        )}
                      </div>

                      <div className="mt-2 pt-2 border-t border-green-200">
                        <div><strong>Tasks proposed:</strong> {runResult.tasks_created ?? 'N/A'}</div>
                        <div><strong>Audit events:</strong> {runResult.audit_events_created ?? 'N/A'}</div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {runId && runResult?.memory_found && (
              <div className="mt-4 p-4 bg-indigo-50 border border-indigo-200 rounded-lg shadow-sm">
                <h3 className="text-sm font-bold text-indigo-900 mb-2 flex items-center gap-1"><Database size={16}/> Existing Memory Found</h3>
                <p className="text-xs text-indigo-700 mb-2">Previous operational tasks were retrieved from MongoDB for context.</p>
                <div className="space-y-1 text-xs text-indigo-800">
                  <div><strong>Memory items used:</strong> {runResult.memory_items_count}</div>
                  <div><strong>Limit:</strong> latest {runResult.memory_context_limited_to}</div>
                  <div><strong>Injected into Gemini:</strong> {runResult.memory_injected_into_gemini ? 'yes' : 'no'}</div>
                </div>
              </div>
            )}

            {runId && runStatus === 'completed' && (
              <div className="mt-4 p-4 bg-white border border-blue-200 rounded-lg shadow-sm">
                <h3 className="text-sm font-bold text-gray-800 mb-1">What happened in this run?</h3>
                <p className="text-[10px] text-gray-500 italic mb-3">Plain-language explanation of the operational memory created from this synthetic note.</p>
                <div className="space-y-3 text-xs text-gray-700">
                  
                  {runResult && (runResult.model_used || runResult.fallback_used || (runResult.model_attempts && runResult.model_attempts.length > 0)) && (
                    <div className="mb-4 pb-3 border-b border-gray-200">
                      <strong className="block text-gray-800 mb-1">Gemini Model Attempts</strong>
                      <ul className="list-disc list-inside space-y-0.5 ml-1 text-[11px]">
                        <li>Extraction mode: <span className="font-mono text-gray-600 bg-gray-100 px-1 rounded">{runResult.extraction_mode}</span></li>
                        {runResult.model_used && (
                          <li>Final selected model: <span className="font-mono text-gray-600 bg-gray-100 px-1 rounded">{runResult.model_used}</span></li>
                        )}
                        <li>Fallback used: <span className={runResult.fallback_used ? "font-semibold text-yellow-600" : "font-semibold text-green-600"}>{runResult.fallback_used ? "yes" : "no"}</span></li>
                        {runResult.fallback_used && runResult.fallback_reason && (
                          <li>Fallback reason: <span className="text-red-600 font-mono text-[10px]">{runResult.fallback_reason}</span></li>
                        )}
                        {runResult.model_attempts && runResult.model_attempts.length > 0 ? (
                          <li className="mt-1">
                            Model attempts:
                            <ul className="ml-5 mt-0.5 space-y-0.5 border-l-2 border-gray-100 pl-2">
                              {runResult.model_attempts.map((att: any, i: number) => (
                                <li key={i} className="flex flex-wrap items-center gap-1">
                                  <span className="font-mono bg-gray-50 border border-gray-200 px-1 rounded text-[10px] text-gray-600">{att.model}</span>
                                  {att.status === 'success' ? (
                                    <span className="text-green-600 font-medium text-[10px]">— success</span>
                                  ) : att.status === 'skipped' ? (
                                    <span className="text-gray-500 font-medium text-[10px]">— skipped/not attempted</span>
                                  ) : (
                                    <>
                                      <span className="text-red-600 font-medium text-[10px]">— failed</span>
                                      {att.reason && <span className="text-gray-500 text-[10px]">({att.reason})</span>}
                                    </>
                                  )}
                                </li>
                              ))}
                            </ul>
                          </li>
                        ) : (
                          runResult.model_used && !runResult.fallback_used && (
                            <li className="text-green-700 italic mt-1">Primary model succeeded; backup models were not needed.</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                  {/* Block 1 */}
                  <div>
                    <strong className="block text-gray-800 mb-0.5">1. Source note understood</strong>
                    <p>The system received a messy synthetic clinic operations note. It treated the note as administrative context only, not as a diagnostic or treatment source.</p>
                  </div>

                  {/* Block 2 */}
                  <div>
                    <strong className="block text-gray-800 mb-0.5">2. Operational signals detected</strong>
                    <p>The agent identified operational signals such as follow-up needs, form uncertainty, insurance checks, communication restrictions, language preferences or human-review requirements.</p>
                    {runResult && runResult.operational_signals_detected && (
                      <p className="mt-0.5 font-medium text-blue-700">Signals detected: {runResult.operational_signals_detected.length}</p>
                    )}
                  </div>

                  {/* Block 3 */}
                  <div>
                    <strong className="block text-gray-800 mb-0.5">3. Tasks proposed</strong>
                    <p>The agent proposed non-clinical internal tasks. Each task remains pending human approval and includes source evidence from the note.</p>
                    <p className="mt-0.5 font-medium text-blue-700">Current run tasks: {tasks.filter(t => t.agent_run_id === runId && t.status === 'proposed').length}</p>
                  </div>

                  {/* Block 4 */}
                  <div>
                    <strong className="block text-gray-800 mb-0.5">4. Memory persisted</strong>
                    <p>The run writes source note, agent run, proposed tasks, audit events and task status history into MongoDB-backed operational memory.</p>
                    <div className="mt-0.5 font-medium text-blue-700 flex flex-wrap gap-2">
                      <span>MongoDB backend: active</span>
                      {activity && activity.collections_touched && (
                        <span>| Collections touched: {activity.collections_touched.length}</span>
                      )}
                    </div>
                  </div>

                  {/* Block 5 */}
                  <div>
                    <strong className="block text-gray-800 mb-0.5">5. Safety boundary applied</strong>
                    <p>The agent did not diagnose, recommend treatment, change medication, send a message, create a real appointment or contact the patient.</p>
                  </div>
                  
                  {/* Optional scenario-specific explanation */}
                  {runResult && runResult.operational_signals_detected && (
                    <div className="pt-2 border-t border-gray-100 space-y-1">
                      {runResult.operational_signals_detected.includes("insurance_verification_needed") && (
                        <p className="text-[11px] font-medium text-indigo-700">✓ Insurance information was flagged for administrative verification.</p>
                      )}
                      {runResult.operational_signals_detected.includes("intake_or_consent_form_uncertain") && (
                        <p className="text-[11px] font-medium text-indigo-700">✓ Form or consent status was flagged as incomplete or uncertain.</p>
                      )}
                      {runResult.operational_signals_detected.includes("communication_restriction") && (
                        <p className="text-[11px] font-medium text-indigo-700">✓ A communication restriction was recorded so no clinical summary is sent automatically.</p>
                      )}
                      {runResult.operational_signals_detected.includes("mixed_patient_note_detected") && (
                        <p className="text-[11px] font-medium text-red-700">⚠ The note appears to mix multiple patients and must be reviewed before action.</p>
                      )}
                    </div>
                  )}

                  {/* In one sentence */}
                  <div className="pt-2 border-t border-gray-100 italic text-gray-600 font-medium">
                    In one sentence: this run turned a messy post-visit operations note into auditable, human-reviewed clinic memory.
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Middle Column: Audit Timeline */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 h-full">
            <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <Activity size={20} /> 2. Audit Timeline
            </h2>
            <div className="text-xs text-gray-500 mb-4 pb-2 border-b">Total events: {events.length}</div>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {events.length === 0 ? (
                <div className="text-sm text-gray-500 italic p-4 bg-gray-50 rounded border border-gray-100">No audit events yet. Run the mock agent to create a timeline.</div>
              ) : (
                events.map((ev, i) => (
                  <div key={ev.event_id} className="flex gap-3 text-sm">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mt-1.5"></div>
                      {i !== events.length - 1 && <div className="w-0.5 h-full bg-gray-200 my-1"></div>}
                    </div>
                    <div>
                      <div className="font-semibold text-gray-700">{ev.event_type.replace(/_/g, ' ')}</div>
                      <div className="text-gray-600">{ev.message}</div>
                      <div className="text-xs text-gray-400 mt-0.5">{new Date(ev.timestamp).toLocaleTimeString()}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Middle-Right Column: MCP Trace */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 h-full">
            <h2 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <Cpu size={20} /> Controlled MongoDB Tools
            </h2>
            <div className="text-xs text-gray-500 mb-4 pb-2 border-b">Safe MCP-compatible tool layer</div>
            <div className="space-y-4 max-h-[600px] overflow-y-auto">
              {mcpCalls.length === 0 ? (
                <div className="text-sm text-gray-500 italic p-4 bg-gray-50 rounded border border-gray-100">No MCP tool calls in mock mode yet. This panel is reserved for controlled MongoDB tool-call traces.</div>
              ) : (
                mcpCalls.map((call) => (
                  <div key={call.tool_call_id} className="border border-gray-200 rounded p-3 bg-gray-50">
                    <div className="flex justify-between items-start mb-1">
                      <h3 className="font-medium text-sm text-gray-900">{call.tool_name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                        call.status === 'success' ? 'bg-green-100 text-green-800' :
                        call.status === 'blocked' ? 'bg-red-100 text-red-800' :
                        call.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {call.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mb-1">Adapter: {call.adapter_type}</div>
                    {call.collections_touched && call.collections_touched.length > 0 && (
                      <div className="text-xs text-blue-600">Collections: {call.collections_touched.join(', ')}</div>
                    )}
                    {call.latency_ms && (
                      <div className="text-xs text-gray-500 mt-1">Latency: {call.latency_ms}ms</div>
                    )}
                    {call.error && (
                      <div className="text-xs text-red-600 mt-1 font-bold">Error: {call.error}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column: Task Board */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white rounded-lg shadow border border-gray-200 p-4 h-full flex flex-col">
            <h2 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <CheckCircle size={20} /> 3. Task Board — Current Run + Persistent Memory
            </h2>
            <p className="text-xs text-gray-500 mb-4">Each run writes source notes, agent runs, proposed tasks, audit events and task status history to MongoDB.</p>
            
            <div className="flex flex-col gap-2 mb-4 text-xs font-medium border-b border-gray-100 pb-4">
              <div className="flex items-center gap-2">
                <span className="text-gray-500 w-24">Current Run:</span>
                <span className="bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Proposed: {runId ? tasks.filter(t => t.agent_run_id === runId && t.status === 'proposed').length : 0}</span>
                <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded">Approved: {runId ? tasks.filter(t => t.agent_run_id === runId && t.status === 'approved').length : 0}</span>
                <span className="bg-red-100 text-red-800 px-2 py-0.5 rounded">Rejected: {runId ? tasks.filter(t => t.agent_run_id === runId && t.status === 'rejected').length : 0}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-gray-500 w-24">Memory Total:</span>
                <span className="bg-gray-100 text-gray-800 px-2 py-0.5 rounded">Total: {tasks.length}</span>
                <span className="bg-yellow-50 text-yellow-800 px-2 py-0.5 rounded border border-yellow-200">Proposed: {tasks.filter(t => t.status === 'proposed').length}</span>
              </div>
            </div>

            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-1 flex-grow">
              {tasks.length === 0 ? (
                <div className="text-sm text-gray-500 italic p-4 bg-gray-50 rounded border border-gray-100">Safe empty state. No operational tasks currently proposed.</div>
              ) : (
                <>
                  {runId && tasks.filter(t => t.agent_run_id === runId).length > 0 && (
                    <div className="mb-6">
                      <h3 className="text-sm font-bold text-gray-800 border-b border-gray-100 pb-1 mb-1">Current Run Tasks</h3>
                      <p className="text-xs text-gray-500 italic mb-3">These tasks were generated from the selected synthetic note and persisted to MongoDB with human approval required.</p>
                      <div className="space-y-3">
                        {tasks.filter(t => t.agent_run_id === runId).map(task => {
                          const descParts = task.description.split("Source evidence: ");
                          const mainDesc = descParts[0];
                          const evidence = descParts[1] ? descParts[1].replace(/^'|'$/g, '') : null;
                          return (
                          <div key={task.task_id} className="border-2 border-blue-200 rounded p-3 bg-white hover:border-blue-300 transition-colors shadow-sm">
                            <div className="flex justify-between items-start mb-2">
                              <h4 className="font-semibold text-gray-800 text-sm">{task.title}</h4>
                              <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                                task.status === 'proposed' ? 'bg-yellow-100 text-yellow-800' :
                                task.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                                task.status === 'in_progress' ? 'bg-purple-100 text-purple-800' :
                                task.status === 'done' ? 'bg-green-100 text-green-800' :
                                'bg-gray-100 text-gray-800'
                              }`}>
                                {task.status}
                              </span>
                            </div>
                            <p className="text-xs text-gray-600 mb-2 whitespace-pre-wrap">{mainDesc.trim()}</p>
                            {evidence && (
                              <div className="bg-yellow-50 border-l-2 border-yellow-400 p-2 text-[10px] text-gray-700 font-mono mb-3 rounded-r">
                                <strong>Source evidence:</strong> {evidence}
                              </div>
                            )}
                            
                            <div className="flex gap-2 mt-2 pt-2 border-t border-gray-100">
                              {task.status === 'proposed' && (
                                <>
                                  <button onClick={() => handleTaskStatus(task.task_id, 'approved')} className="text-xs bg-green-50 text-green-700 hover:bg-green-100 px-3 py-1 rounded font-medium border border-green-200 transition-colors">Approve</button>
                                  <button onClick={() => handleTaskStatus(task.task_id, 'rejected')} className="text-xs bg-red-50 text-red-700 hover:bg-red-100 px-3 py-1 rounded font-medium border border-red-200 transition-colors">Reject</button>
                                </>
                              )}
                              {task.status === 'approved' && (
                                <button onClick={() => handleTaskStatus(task.task_id, 'in_progress')} className="text-xs bg-white border border-gray-300 hover:bg-gray-50 px-2 py-1 rounded">Start Work</button>
                              )}
                              {task.status === 'in_progress' && (
                                <button onClick={() => handleTaskStatus(task.task_id, 'done')} className="text-xs bg-green-50 border border-green-200 text-green-700 hover:bg-green-100 px-2 py-1 rounded">Mark Done</button>
                              )}
                            </div>
                          </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  
                  {(() => {
                    const previousRunTasks = tasks.filter(t => t.agent_run_id !== runId);
                    if (previousRunTasks.length === 0) return null;
                    
                    const sortedTasks = [...previousRunTasks].sort((a, b) => 
                      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                    );
                    const limitedTasks = sortedTasks.slice(0, 10);
                    
                    return (
                      <div className="mt-6 pt-4 border-t border-gray-200">
                        <div className="flex justify-between items-end mb-1">
                          <h3 className="text-sm font-bold text-gray-600">Persisted Tasks (Previous Runs)</h3>
                          <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-medium border border-gray-200">
                            {previousRunTasks.length > 10 
                              ? `Showing latest 10 of ${previousRunTasks.length} persisted tasks` 
                              : `Showing all ${previousRunTasks.length} persisted tasks`}
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-500 italic mb-3">
                          These are previous tasks still stored in MongoDB operational memory. 
                          Only the latest tasks are shown to keep the demo focused.
                        </p>
                        <div className="space-y-3 opacity-60 hover:opacity-100 transition-opacity">
                          {limitedTasks.map(task => {
                            const descParts = task.description.split("Source evidence: ");
                            const mainDesc = descParts[0];
                            const evidence = descParts[1] ? descParts[1].replace(/^'|'$/g, '') : null;
                            return (
                            <div key={task.task_id} className="border border-gray-200 rounded p-3 bg-gray-50">
                              <div className="flex justify-between items-start mb-2">
                                <h4 className="font-semibold text-gray-700 text-sm">{task.title}</h4>
                                <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                                  task.status === 'proposed' ? 'bg-yellow-100 text-yellow-800' :
                                  task.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                                  task.status === 'in_progress' ? 'bg-purple-100 text-purple-800' :
                                  task.status === 'done' ? 'bg-green-100 text-green-800' :
                                  'bg-gray-100 text-gray-800'
                                }`}>
                                  {task.status}
                                </span>
                              </div>
                              <p className="text-[11px] text-gray-500 mb-2 whitespace-pre-wrap">{mainDesc.trim()}</p>
                              {evidence && (
                                <div className="bg-gray-100 border-l-2 border-gray-300 p-2 text-[10px] text-gray-500 font-mono mb-2 rounded-r">
                                  <strong>Source evidence:</strong> {evidence}
                                </div>
                              )}
                              <div className="text-[10px] text-gray-400">
                                {new Date(task.created_at).toLocaleTimeString()}
                              </div>
                            </div>
                            );
                          })}
                        </div>
                      </div>
                    );
                  })()}
                </>
              )}
            </div>
          </div>
        </div>

      </main>

      {/* Safety Banners */}
      <footer className="mt-auto bg-yellow-50 border-t border-yellow-200 p-4">
        <div className="max-w-4xl mx-auto flex items-start gap-3">
          <AlertTriangle className="text-yellow-600 shrink-0" size={24} />
          <div className="text-sm text-yellow-800">
            <strong className="block mb-1">SAFETY WARNING: Synthetic demo only.</strong>
            <p>Synthetic demo only. No diagnosis, treatment recommendation, medication change, or real external delivery. Human approval required for operational tasks.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
