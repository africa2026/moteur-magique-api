import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Search, 
  BookOpen, 
  Sparkles, 
  MessageSquare, 
  FileText, 
  Library, 
  History, 
  Settings, 
  Globe, 
  Wifi, 
  WifiOff,
  TrendingUp,
  Zap,
  Cpu,
  Database,
  Trophy,
  Target,
  Share2,
  Maximize2,
  Upload,
  Cloud,
  HardDrive
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "";

export default function Home() {
  const [query, setQuery] = useState("");
  const [isOnline, setIsOnline] = useState(true);
  const [activeTab, setActiveTab] = useState("search");
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [systemLoad, setSystemLoad] = useState(34);
  const [knowledgeScore, setKnowledgeScore] = useState(1250);
  const [error, setError] = useState<string | null>(null);
  const [isDriveConnected, setIsDriveConnected] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  // Arena state
  const [thinkerA, setThinkerA] = useState("don_bosco");
  const [thinkerB, setThinkerB] = useState("maria_montessori");
  const [arenaTheme, setArenaTheme] = useState("");
  const [arenaResult, setArenaResult] = useState<any>(null);
  const [arenaLoading, setArenaLoading] = useState(false);
  const [showAddThinker, setShowAddThinker] = useState(false);
  const [newThinker, setNewThinker] = useState({ full_name: "", birth_year: "", death_year: "", work_title: "", work_year: "" });
  const [customThinkers, setCustomThinkers] = useState<any[]>([]);

  // Fusion state
  const [conceptA, setConceptA] = useState("");
  const [conceptB, setConceptB] = useState("");
  const [fusionResult, setFusionResult] = useState<any>(null);
  const [fusionLoading, setFusionLoading] = useState(false);

  // Council state
  const [councilQuestion, setCouncilQuestion] = useState("");
  const [selectedSages, setSelectedSages] = useState(["theologian", "pedagogue", "philosopher"]);
  const [councilResult, setCouncilResult] = useState<any>(null);
  const [councilLoading, setCouncilLoading] = useState(false);

  // Simulate system activity
  useEffect(() => {
    const interval = setInterval(() => {
      setSystemLoad(prev => Math.min(98, Math.max(20, prev + (Math.random() * 10 - 5))));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    setError(null);
    setResults([]);

    try {
      // REAL API CALL
      const response = await fetch(`${API_URL}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          query: query,
          mode: "deep_research", // Enable deep research mode
          sources: ["corpus_salesiano", "semantic_scholar", "wikipedia", "uploaded_docs", "google_drive"] 
        }),
      });

      if (!response.ok) {
        throw new Error(`Errore server: ${response.status}`);
      }

      const data = await response.json();
      
      const rawResults = data.results?.results || data.results || [];
      const resultArray = Array.isArray(rawResults) ? rawResults : [];
      const transformedResults = resultArray.map((item: any, index: number) => ({
        title: item.title || "Documento senza titolo",
        source: item.source || "Fonte sconosciuta",
        type: item.type || "DOCUMENTO",
        relevance: Math.round((item.confidence || item.score || 0) * 1), // Use confidence directly if available
        snippet: item.snippet || item.content?.substring(0, 300) + "...",
        citations: item.citations || 0,
        url: item.url
      }));

      setResults(transformedResults);
      setKnowledgeScore(prev => prev + (transformedResults.length * 50));
      
    } catch (err) {
      console.error("Search error:", err);
      setError("Errore di connessione al cervello centrale. Riprovare.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleFileUpload = () => {
    // Simulate file upload for UI demo
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.docx,.txt';
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      if (file) {
        setUploadedFiles(prev => [...prev, file.name]);
        // In real implementation, this would upload to backend
      }
    };
    input.click();
  };

  const thinkerOptions = [
    { id: "don_bosco", name: "Don Bosco" },
    { id: "maria_montessori", name: "Maria Montessori" },
    { id: "paulo_freire", name: "Paulo Freire" },
    { id: "hannah_arendt", name: "Hannah Arendt" },
    { id: "tommaso_aquino", name: "Tommaso d'Aquino" },
    { id: "jean_piaget", name: "Jean Piaget" },
    { id: "lev_vygotsky", name: "Lev Vygotsky" },
    { id: "edith_stein", name: "Edith Stein" },
    ...customThinkers,
  ];

  useEffect(() => {
    fetch(`${API_URL}/api/advanced/thinkers`).then(r => r.json()).then(data => {
      if (data.success && data.thinkers) {
        const builtinIds = ["don_bosco","maria_montessori","paulo_freire","hannah_arendt","tommaso_aquino","jean_piaget","lev_vygotsky","edith_stein"];
        const custom = data.thinkers.filter((t: any) => !builtinIds.includes(t.id)).map((t: any) => ({ id: t.id, name: t.name }));
        setCustomThinkers(custom);
      }
    }).catch(() => {});
  }, []);

  const handleAddThinker = async () => {
    if (!newThinker.full_name.trim()) return;
    try {
      const works = newThinker.work_title ? [{ title: newThinker.work_title, year: parseInt(newThinker.work_year) || 2000, type: "book" }] : [];
      const resp = await fetch(`${API_URL}/api/advanced/thinkers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: newThinker.full_name,
          birth_year: parseInt(newThinker.birth_year) || 0,
          death_year: parseInt(newThinker.death_year) || 0,
          key_works: works,
        }),
      });
      const data = await resp.json();
      if (data.success) {
        setCustomThinkers(prev => [...prev, { id: data.id, name: newThinker.full_name }]);
        setNewThinker({ full_name: "", birth_year: "", death_year: "", work_title: "", work_year: "" });
        setShowAddThinker(false);
      }
    } catch (err) { console.error("Add thinker error:", err); }
  };

  const sageOptions = [
    { id: "theologian", name: "Teologo" },
    { id: "pedagogue", name: "Pedagogo" },
    { id: "philosopher", name: "Filosofo" },
    { id: "sociologist", name: "Sociologo" },
    { id: "historian", name: "Storico" },
    { id: "psychologist", name: "Psicologo" },
  ];

  const handleArenaDebate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!arenaTheme.trim()) return;
    setArenaLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/advanced/arena/debate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ thinker_a: thinkerA, thinker_b: thinkerB, theme: arenaTheme, language: "it", citation_style: "apa" }),
      });
      if (!response.ok) throw new Error(`Errore server: ${response.status}`);
      const data = await response.json();
      setArenaResult(data);
      setKnowledgeScore(prev => prev + 200);
    } catch (err) {
      console.error("Arena error:", err);
      setError("Errore di connessione all'Arena Dialectica. Riprovare.");
    } finally {
      setArenaLoading(false);
    }
  };

  const handleFusion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!conceptA.trim() || !conceptB.trim()) return;
    setFusionLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/advanced/fusion/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ concept_a: conceptA, concept_b: conceptB, language: "it", citation_style: "apa" }),
      });
      if (!response.ok) throw new Error(`Errore server: ${response.status}`);
      const data = await response.json();
      setFusionResult(data);
      setKnowledgeScore(prev => prev + 300);
    } catch (err) {
      console.error("Fusion error:", err);
      setError("Errore di connessione alla Fusion Temporelle. Riprovare.");
    } finally {
      setFusionLoading(false);
    }
  };

  const handleCouncil = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!councilQuestion.trim()) return;
    setCouncilLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/advanced/council/convene`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: councilQuestion, sages: selectedSages, language: "it", citation_style: "apa" }),
      });
      if (!response.ok) throw new Error(`Errore server: ${response.status}`);
      const data = await response.json();
      setCouncilResult(data);
      setKnowledgeScore(prev => prev + 250);
    } catch (err) {
      console.error("Council error:", err);
      setError("Errore di connessione al Consiglio dei Saggi. Riprovare.");
    } finally {
      setCouncilLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col font-sans text-foreground overflow-hidden selection:bg-primary selection:text-primary-foreground">
      
      {/* Top HUD Bar */}
      <header className="h-14 border-b border-border bg-background/90 backdrop-blur-md flex items-center justify-between px-4 sticky top-0 z-50 shadow-lg shadow-primary/5">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-primary animate-pulse">
            <Cpu className="w-5 h-5" />
            <span className="font-tech font-bold tracking-widest text-lg">MOTEUR v4.0</span>
          </div>
          <div className="h-6 w-px bg-border mx-2"></div>
          <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground">
            <span className={isOnline ? "text-green-500" : "text-amber-500"}>●</span>
            {isOnline ? "SYSTEM ONLINE" : "OFFLINE MODE"}
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-3">
            <div className="text-right">
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider">System Load</div>
              <div className="font-mono text-accent font-bold">{Math.round(systemLoad)}%</div>
            </div>
            <div className="w-24 h-1.5 bg-secondary rounded-full overflow-hidden">
              <div 
                className="h-full bg-accent transition-all duration-500 ease-out"
                style={{ width: `${systemLoad}%` }}
              ></div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-primary hover:bg-primary/10">
              <Settings className="w-5 h-5" />
            </Button>
            <div className="w-8 h-8 rounded bg-primary/20 border border-primary flex items-center justify-center text-primary font-bold font-tech">
              AO
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Command Panel */}
        <aside className="w-20 md:w-64 bg-sidebar border-r border-border flex flex-col z-40 hidden md:flex">
          <div className="p-4 space-y-2">
            <Button 
              variant={activeTab === "search" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "search" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("search")}
            >
              <Search className="w-5 h-5" />
              <span className="hidden md:inline">RICERCA</span>
            </Button>
            <Button 
              variant={activeTab === "arena" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "arena" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("arena")}
            >
              <Zap className="w-5 h-5" />
              <span className="hidden md:inline">ARENA</span>
            </Button>
            <Button 
              variant={activeTab === "fusion" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "fusion" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("fusion")}
            >
              <Sparkles className="w-5 h-5" />
              <span className="hidden md:inline">FUSION</span>
            </Button>
            <Button 
              variant={activeTab === "council" ? "secondary" : "ghost"} 
              className={`w-full justify-start gap-3 h-12 font-tech tracking-wide ${activeTab === "council" ? "bg-primary/10 text-primary border border-primary/20" : "text-muted-foreground hover:text-foreground"}`}
              onClick={() => setActiveTab("council")}
            >
              <Globe className="w-5 h-5" />
              <span className="hidden md:inline">CONSIGLIO</span>
            </Button>
          </div>

          <div className="mt-auto p-4 border-t border-border">
            <Card className="bg-card border-primary/20 shadow-[0_0_15px_rgba(251,191,36,0.1)]">
              <CardContent className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-tech text-muted-foreground uppercase">Knowledge Score</span>
                  <Trophy className="w-4 h-4 text-primary" />
                </div>
                <div className="text-2xl font-mono font-bold text-primary mb-1">{knowledgeScore}</div>
                <div className="text-[10px] text-muted-foreground">Livello: <span className="text-accent">MASTER</span></div>
              </CardContent>
            </Card>
          </div>
        </aside>

        {/* Main Arena */}
        <main className="flex-1 relative overflow-hidden flex flex-col">
          {/* Background Grid Effect */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:40px_40px] opacity-20 pointer-events-none"></div>
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,#0f172a_100%)] pointer-events-none"></div>

          <ScrollArea className="flex-1 p-6 md:p-10 z-10">
            <div className="max-w-5xl mx-auto space-y-10 pb-20">
              
              {/* Hero Section */}
              <div className="text-center space-y-6 py-10 relative">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none"></div>
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 px-4 py-1 font-mono tracking-widest">
                  KNOWLEDGE ARENA ONLINE
                </Badge>
                <h1 className="text-5xl md:text-7xl font-bold text-white tracking-tight drop-shadow-[0_0_15px_rgba(251,191,36,0.3)]">
                  COMANDI <span className="text-primary">ATTIVI</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-2xl mx-auto font-light font-tech tracking-wide">
                  Accesso a 12 motori accademici e corpus salesiano. In attesa di input.
                </p>
              </div>

              {/* Central Command Input */}
              <div className="relative max-w-3xl mx-auto group">
                <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent to-primary rounded-lg opacity-30 group-hover:opacity-70 blur transition duration-500 animate-pulse"></div>
                <form onSubmit={handleSearch} className="relative bg-background border border-primary/30 rounded-lg flex items-center p-2 shadow-2xl">
                  <div className="pl-4 pr-2 text-primary">
                    <Target className="w-6 h-6" />
                  </div>
                  <Input 
                    className="border-none shadow-none focus-visible:ring-0 text-xl h-14 bg-transparent placeholder:text-muted-foreground/30 font-tech tracking-wide text-white" 
                    placeholder="INSERIRE PARAMETRI DI RICERCA..." 
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                  <Button 
                    type="submit" 
                    size="lg" 
                    className="h-12 px-8 bg-primary text-primary-foreground hover:bg-primary/90 font-bold tracking-wider font-tech rounded-md shadow-[0_0_20px_rgba(251,191,36,0.4)] transition-all hover:scale-105" 
                    disabled={isSearching}
                  >
                    {isSearching ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></span>
                        SCANNING...
                      </span>
                    ) : (
                      "ESEGUI"
                    )}
                  </Button>
                </form>
                
                {/* Search Stats & Personal Sources */}
                <div className="flex justify-between mt-4 px-2 font-mono text-xs text-muted-foreground">
                  <div className="flex gap-4 items-center">
                    <span className="flex items-center gap-1 text-accent"><Database className="w-3 h-3" /> 12 FONTI CONNESSE</span>
                    
                    {/* Uploaded Files Indicator */}
                    {uploadedFiles.length > 0 && (
                      <span className="flex items-center gap-1 text-green-400 animate-pulse">
                        <FileText className="w-3 h-3" /> {uploadedFiles.length} DOCS PERSONALI
                      </span>
                    )}

                    {/* Drive Indicator */}
                    {isDriveConnected && (
                      <span className="flex items-center gap-1 text-blue-400 animate-pulse">
                        <Cloud className="w-3 h-3" /> DRIVE CONNESSO
                      </span>
                    )}
                  </div>
                  <span className="text-muted-foreground/50">LATENCY: 12ms</span>
                </div>
              </div>

              {/* Personal Sources Control Panel */}
              <div className="max-w-3xl mx-auto grid grid-cols-2 gap-4">
                <Button 
                  variant="outline" 
                  className="h-12 border-primary/20 hover:bg-primary/10 hover:border-primary/50 text-muted-foreground hover:text-primary transition-all group"
                  onClick={handleFileUpload}
                >
                  <Upload className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                  <span className="font-tech tracking-wide">UPLOAD DOCUMENTI</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className={`h-12 border-primary/20 hover:bg-primary/10 hover:border-primary/50 transition-all group ${isDriveConnected ? "text-blue-400 border-blue-500/30 bg-blue-500/5" : "text-muted-foreground hover:text-primary"}`}
                  onClick={() => setIsDriveConnected(!isDriveConnected)}
                >
                  <Cloud className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                  <span className="font-tech tracking-wide">{isDriveConnected ? "DRIVE CONNESSO" : "CONNETTI DRIVE"}</span>
                </Button>
              </div>

              {/* Error Message */}
              {error && (
                <div className="max-w-3xl mx-auto bg-destructive/10 border border-destructive/50 text-destructive p-4 rounded-lg flex items-center gap-3 animate-in fade-in slide-in-from-top-4">
                  <WifiOff className="w-5 h-5" />
                  <span className="font-mono">{error}</span>
                </div>
              )}

              {/* === TAB: SEARCH (original) === */}
              {activeTab === "search" && (
                <>
                  {results.length > 0 && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
                      <div className="flex items-center justify-between border-b border-border pb-4">
                        <h3 className="font-tech text-2xl font-bold text-white flex items-center gap-2">
                          <span className="w-2 h-8 bg-primary rounded-sm"></span>
                          RISULTATI ANALISI
                        </h3>
                        <Badge variant="outline" className="font-mono border-accent text-accent bg-accent/10">
                          {results.length} MATCH TROVATI
                        </Badge>
                      </div>
                      <div className="grid gap-4">
                        {results.map((result: any, index: number) => (
                          <Card key={index} className="group bg-card border-l-4 border-l-primary border-y border-r border-border hover:border-primary/50 transition-all duration-300 overflow-hidden relative">
                            <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                              <Button size="sm" variant="outline" className="border-primary text-primary hover:bg-primary hover:text-primary-foreground font-mono text-xs" onClick={() => window.open(result.url, '_blank')}>
                                <Maximize2 className="w-3 h-3 mr-1" /> ESPANDI
                              </Button>
                            </div>
                            <CardHeader className="pb-2">
                              <div className="space-y-1">
                                <div className="flex items-center gap-2 mb-2">
                                  <Badge variant="secondary" className="bg-primary/20 text-primary border-none font-mono text-[10px] tracking-wider">{result.type}</Badge>
                                  <span className="text-xs font-mono text-muted-foreground">RILEVANZA: <span className="text-accent">{result.relevance}%</span></span>
                                  <Progress value={result.relevance} className="w-20 h-1.5 bg-secondary [&>div]:bg-accent" />
                                </div>
                                <CardTitle className="font-tech text-xl text-white group-hover:text-primary transition-colors">{result.title}</CardTitle>
                                <CardDescription className="flex items-center gap-2 text-sm font-mono">
                                  <span className="text-accent">{result.source}</span>
                                </CardDescription>
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="bg-secondary/50 p-3 rounded border border-white/5 font-mono text-sm text-muted-foreground leading-relaxed">
                                <span className="text-primary mr-2">{">"}</span>{result.snippet}
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* === TAB: ARENA DIALECTICA - GAMIFIED === */}
              {activeTab === "arena" && (
                <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in">
                  <div className="text-center space-y-3 relative">
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-red-500/5 rounded-full blur-[80px] pointer-events-none"></div>
                    <Badge variant="outline" className="bg-red-500/10 text-red-400 border-red-500/30 px-6 py-2 font-mono tracking-[0.3em] text-lg animate-pulse">ARENA DIALECTICA</Badge>
                    <h2 className="text-4xl md:text-5xl font-bold text-white font-tech tracking-tight">BATTAGLIA delle IDEE</h2>
                    <p className="text-muted-foreground font-mono text-sm">Scegli i tuoi campioni. Lancia il dibattito. Scopri la sintesi.</p>
                  </div>

                  <form onSubmit={handleArenaDebate} className="space-y-6">
                    <div className="grid grid-cols-5 gap-4 items-center">
                      <div className="col-span-2">
                        <div className="text-center mb-2">
                          <span className="text-xs font-mono text-red-400 tracking-widest">CAMPIONE A</span>
                        </div>
                        <select value={thinkerA} onChange={e => setThinkerA(e.target.value)} className="w-full h-14 bg-red-500/5 border-2 border-red-500/30 rounded-lg px-3 text-white font-tech text-lg text-center hover:border-red-500/60 transition-all">
                          {thinkerOptions.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                        </select>
                      </div>
                      <div className="text-center">
                        <div className="w-16 h-16 mx-auto rounded-full bg-red-500/20 border-2 border-red-500/50 flex items-center justify-center text-3xl font-bold text-red-400 animate-pulse shadow-[0_0_30px_rgba(239,68,68,0.3)]">VS</div>
                      </div>
                      <div className="col-span-2">
                        <div className="text-center mb-2">
                          <span className="text-xs font-mono text-blue-400 tracking-widest">CAMPIONE B</span>
                        </div>
                        <select value={thinkerB} onChange={e => setThinkerB(e.target.value)} className="w-full h-14 bg-blue-500/5 border-2 border-blue-500/30 rounded-lg px-3 text-white font-tech text-lg text-center hover:border-blue-500/60 transition-all">
                          {thinkerOptions.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                        </select>
                      </div>
                    </div>
                    <Input placeholder="TEMA DELLA BATTAGLIA..." value={arenaTheme} onChange={e => setArenaTheme(e.target.value)} className="h-16 bg-background border-2 border-white/20 text-white font-tech text-xl text-center tracking-wide placeholder:text-white/20" />
                    <Button type="submit" disabled={arenaLoading} className="w-full h-16 bg-gradient-to-r from-red-600 via-purple-600 to-blue-600 text-white font-bold font-tech tracking-[0.2em] text-xl rounded-lg shadow-[0_0_40px_rgba(147,51,234,0.4)] hover:shadow-[0_0_60px_rgba(147,51,234,0.6)] transition-all hover:scale-[1.02]">
                      {arenaLoading ? (
                        <span className="flex items-center gap-3">
                          <span className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin"></span>
                          BATTAGLIA IN CORSO...
                        </span>
                      ) : "FIGHT!"}
                    </Button>
                  </form>

                  <div className="flex justify-center">
                    <Button variant="outline" size="sm" onClick={() => setShowAddThinker(!showAddThinker)} className="text-muted-foreground hover:text-primary border-dashed border-white/20 hover:border-primary/50 font-mono text-xs">
                      + AGGIUNGI PENSATORE PERSONALIZZATO
                    </Button>
                  </div>

                  {showAddThinker && (
                    <Card className="bg-card border border-primary/20 animate-in fade-in slide-in-from-top-4">
                      <CardHeader className="pb-2">
                        <CardTitle className="font-tech text-primary text-sm tracking-widest">NUOVO PENSATORE</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <Input placeholder="Nome completo (es: Jacques Maritain)" value={newThinker.full_name} onChange={e => setNewThinker(p => ({...p, full_name: e.target.value}))} className="bg-background border-white/20 text-white" />
                        <div className="grid grid-cols-2 gap-3">
                          <Input placeholder="Anno nascita" type="number" value={newThinker.birth_year} onChange={e => setNewThinker(p => ({...p, birth_year: e.target.value}))} className="bg-background border-white/20 text-white" />
                          <Input placeholder="Anno morte (0 se vivente)" type="number" value={newThinker.death_year} onChange={e => setNewThinker(p => ({...p, death_year: e.target.value}))} className="bg-background border-white/20 text-white" />
                        </div>
                        <div className="grid grid-cols-3 gap-3">
                          <Input placeholder="Opera principale" value={newThinker.work_title} onChange={e => setNewThinker(p => ({...p, work_title: e.target.value}))} className="col-span-2 bg-background border-white/20 text-white" />
                          <Input placeholder="Anno" type="number" value={newThinker.work_year} onChange={e => setNewThinker(p => ({...p, work_year: e.target.value}))} className="bg-background border-white/20 text-white" />
                        </div>
                        <Button onClick={handleAddThinker} className="w-full bg-primary text-primary-foreground font-tech">SALVA PENSATORE</Button>
                      </CardContent>
                    </Card>
                  )}

                  {arenaResult && arenaResult.success && (
                    <div className="space-y-6">
                      {arenaResult.rounds?.map((round: any, i: number) => {
                        const isA = i % 2 === 0;
                        const color = isA ? "red" : "blue";
                        const roundLabels = ["APERTURA", "RISPOSTA", "CONTRATTACCO", "APPROFONDIMENTO", "FINALE"];
                        return (
                          <div key={i} className={`animate-in fade-in slide-in-from-${isA ? 'left' : 'right'}-8`} style={{animationDelay: `${i * 200}ms`}}>
                            <div className={`flex items-center gap-3 mb-3 ${isA ? '' : 'flex-row-reverse'}`}>
                              <div className={`w-12 h-12 rounded-full bg-${color}-500/20 border-2 border-${color}-500/50 flex items-center justify-center font-bold text-${color}-400 text-lg shadow-[0_0_15px_rgba(${isA ? '239,68,68' : '59,130,246'},0.3)]`}>
                                {round.speaker?.split(' ').map((w: string) => w[0]).join('').slice(0,2)}
                              </div>
                              <div className={isA ? '' : 'text-right'}>
                                <div className="flex items-center gap-2">
                                  <Badge className={`bg-${color}-500/20 text-${color}-400 border-${color}-500/30 font-mono text-[10px]`}>ROUND {round.round}</Badge>
                                  <span className="text-[10px] font-mono text-muted-foreground/50 uppercase">{roundLabels[i] || ""}</span>
                                </div>
                                <span className="font-tech font-bold text-white text-lg">{round.speaker}</span>
                              </div>
                            </div>
                            <Card className={`bg-card/80 backdrop-blur border-l-4 border-${color}-500/50 shadow-[0_0_20px_rgba(${isA ? '239,68,68' : '59,130,246'},0.1)]`}>
                              <CardContent className="p-5">
                                <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap text-[15px]">{round.text}</p>
                              </CardContent>
                            </Card>
                          </div>
                        );
                      })}

                      <div className="relative py-8">
                        <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-primary/30"></div></div>
                        <div className="relative flex justify-center">
                          <span className="bg-background px-6 py-2 rounded-full border-2 border-primary text-primary font-tech tracking-[0.3em] text-sm shadow-[0_0_30px_rgba(251,191,36,0.3)] animate-pulse">SINTESI INEDITA</span>
                        </div>
                      </div>

                      <Card className="bg-gradient-to-br from-primary/10 via-card to-accent/10 border-2 border-primary shadow-[0_0_50px_rgba(251,191,36,0.15)]">
                        <CardContent className="p-8 space-y-6">
                          <div className="flex justify-center mb-4">
                            <Sparkles className="w-10 h-10 text-primary animate-pulse" />
                          </div>
                          <p className="text-white leading-relaxed whitespace-pre-wrap text-lg text-center">{arenaResult.synthesis}</p>
                          <div className="border-t border-border pt-6 mt-6">
                            <h4 className="font-tech text-primary text-xs tracking-widest mb-3">BIBLIOGRAFIA</h4>
                            <p className="text-xs font-mono text-muted-foreground whitespace-pre-wrap">{arenaResult.bibliography}</p>
                          </div>
                          <p className="text-[10px] font-mono text-muted-foreground/40 italic text-center">{arenaResult.provenance_note}</p>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </div>
              )}

              {/* === TAB: FUSION TEMPORELLE === */}
              {activeTab === "fusion" && (
                <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in">
                  <div className="text-center space-y-3">
                    <Badge variant="outline" className="bg-accent/10 text-accent border-accent/30 px-4 py-1 font-mono tracking-widest">FUSION TEMPORELLE</Badge>
                    <h2 className="text-3xl font-bold text-white font-tech">Collisione di Concetti</h2>
                    <p className="text-muted-foreground font-mono text-sm">Due idee, un neologismo, un nuovo mondo</p>
                  </div>

                  <form onSubmit={handleFusion} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <Input placeholder="CONCETTO A (es: amorevolezza)" value={conceptA} onChange={e => setConceptA(e.target.value)} className="h-14 bg-background border-accent/30 text-white font-tech text-lg" />
                      <Input placeholder="CONCETTO B (es: intelligenza emotiva)" value={conceptB} onChange={e => setConceptB(e.target.value)} className="h-14 bg-background border-accent/30 text-white font-tech text-lg" />
                    </div>
                    <Button type="submit" disabled={fusionLoading} className="w-full h-14 bg-accent text-accent-foreground font-bold font-tech tracking-wider text-lg">
                      {fusionLoading ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-accent-foreground/30 border-t-accent-foreground rounded-full animate-spin"></span>FUSIONE IN CORSO...</span> : "FONDI I CONCETTI"}
                    </Button>
                  </form>

                  {fusionResult && fusionResult.success && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8">
                      <Card className="bg-card border-2 border-accent shadow-[0_0_30px_rgba(251,191,36,0.2)]">
                        <CardHeader>
                          <Badge variant="secondary" className="w-fit bg-accent/20 text-accent font-mono text-lg px-4 py-1">{fusionResult.neologismo}</Badge>
                          <CardDescription className="text-muted-foreground italic mt-2">{fusionResult.etimologia}</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                          <div className="bg-secondary/50 p-4 rounded border border-accent/20">
                            <h4 className="font-tech text-accent text-sm mb-2">DEFINIZIONE</h4>
                            <p className="text-white font-medium">{fusionResult.definizione}</p>
                          </div>
                          <div>
                            <h4 className="font-tech text-accent text-sm mb-3">MINI-SAGGIO</h4>
                            <p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">{fusionResult.mini_saggio}</p>
                          </div>
                          {fusionResult.applicazioni && (
                            <div>
                              <h4 className="font-tech text-accent text-sm mb-3">APPLICAZIONI PRATICHE</h4>
                              <div className="grid gap-2">
                                {fusionResult.applicazioni.map((app: string, i: number) => (
                                  <div key={i} className="flex items-start gap-2 bg-secondary/30 p-3 rounded">
                                    <TrendingUp className="w-4 h-4 text-accent mt-0.5 shrink-0" />
                                    <span className="text-muted-foreground text-sm">{app}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          <div className="border-t border-border pt-4">
                            <p className="text-xs font-mono text-muted-foreground whitespace-pre-wrap">{fusionResult.bibliography}</p>
                          </div>
                          <p className="text-[10px] font-mono text-muted-foreground/50 italic">{fusionResult.provenance_note}</p>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </div>
              )}

              {/* === TAB: CONSEIL DES SAGES === */}
              {activeTab === "council" && (
                <div className="max-w-4xl mx-auto space-y-8 animate-in fade-in">
                  <div className="text-center space-y-3">
                    <Badge variant="outline" className="bg-white/10 text-white border-white/30 px-4 py-1 font-mono tracking-widest">CONSIGLIO DEI SAGGI</Badge>
                    <h2 className="text-3xl font-bold text-white font-tech">Panel Multidisciplinare</h2>
                    <p className="text-muted-foreground font-mono text-sm">Una domanda, molte prospettive, piste inedite</p>
                  </div>

                  <form onSubmit={handleCouncil} className="space-y-4">
                    <Input placeholder="LA TUA DOMANDA COMPLESSA..." value={councilQuestion} onChange={e => setCouncilQuestion(e.target.value)} className="h-14 bg-background border-white/30 text-white font-tech text-lg" />
                    <div>
                      <label className="text-xs font-mono text-muted-foreground mb-2 block">SELEZIONA I SAGGI (clicca per attivare/disattivare)</label>
                      <div className="flex flex-wrap gap-2">
                        {sageOptions.map(sage => (
                          <Button key={sage.id} type="button" variant={selectedSages.includes(sage.id) ? "secondary" : "outline"} size="sm"
                            className={selectedSages.includes(sage.id) ? "bg-primary/20 text-primary border-primary/30" : "text-muted-foreground"}
                            onClick={() => setSelectedSages(prev => prev.includes(sage.id) ? prev.filter(s => s !== sage.id) : [...prev, sage.id])}
                          >{sage.name}</Button>
                        ))}
                      </div>
                    </div>
                    <Button type="submit" disabled={councilLoading} className="w-full h-14 bg-white/10 border border-white/30 text-white font-bold font-tech tracking-wider text-lg hover:bg-white/20">
                      {councilLoading ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>CONVOCAZIONE IN CORSO...</span> : "CONVOCA IL CONSIGLIO"}
                    </Button>
                  </form>

                  {councilResult && councilResult.success && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-8">
                      {councilResult.sages?.map((sage: any, i: number) => (
                        <Card key={i} className="bg-card border-l-4 border-l-white/30">
                          <CardHeader className="pb-2">
                            <span className="font-tech font-bold text-white">{sage.sage_name}</span>
                          </CardHeader>
                          <CardContent><p className="text-muted-foreground leading-relaxed whitespace-pre-wrap">{sage.response}</p></CardContent>
                        </Card>
                      ))}

                      <Card className="bg-card border-2 border-white/50 shadow-[0_0_30px_rgba(255,255,255,0.1)]">
                        <CardHeader>
                          <div className="flex items-center gap-2">
                            <Globe className="w-5 h-5 text-white" />
                            <CardTitle className="font-tech text-white">SINTESI DEL MODERATORE</CardTitle>
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          <p className="text-white leading-relaxed whitespace-pre-wrap">{councilResult.synthesis}</p>
                          <div className="border-t border-border pt-4">
                            <p className="text-xs font-mono text-muted-foreground whitespace-pre-wrap">{councilResult.bibliography}</p>
                          </div>
                          <p className="text-[10px] font-mono text-muted-foreground/50 italic">{councilResult.provenance_note}</p>
                        </CardContent>
                      </Card>
                    </div>
                  )}
                </div>
              )}
            </div>
          </ScrollArea>
        </main>
      </div>
    </div>
  );
}
