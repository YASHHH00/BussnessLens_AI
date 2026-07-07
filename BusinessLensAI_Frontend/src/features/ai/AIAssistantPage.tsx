import React, { useState, useRef, useEffect } from 'react';
import { Sparkles, Send, Bot, User, ArrowRight, CheckCircle2, Calculator, Database, ShieldCheck, Plus, Download, RefreshCw, BarChart3, Table as TableIcon, Layers, FileText } from 'lucide-react';
import { Button, Input, Card, CardContent, Badge, DataTable, ChartWrapper, ExplainabilityPanel, toast, DomainSelector } from '../../shared/components';
import { useAppStore } from '../../shared/stores/useAppStore';

interface ChatMessage {
  id: string;
  sender: 'USER' | 'AI';
  text: string;
  timestamp: string;
  isStreaming?: boolean;
  chart?: {
    title: string;
    type: 'bar' | 'line' | 'pie';
    data: { name: string; value: number }[];
  };
  table?: {
    columns: { key: string; header: string }[];
    rows: Record<string, any>[];
  };
  reasoningTrail?: {
    businessRules: string[];
    semanticMapping: string;
    sqlQuery: string;
    confidence: number;
    summary: string;
  };
}

export const AIAssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'msg_init',
      sender: 'AI',
      text: "Hello! I am BusinessLens AI, your enterprise analytical co-pilot. I have loaded your PostgreSQL retail schema and confirmed semantic mappings. What business questions or anomalies would you like to investigate today?",
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [explainModalOpen, setExplainModalOpen] = useState(false);
  const [selectedMsgId, setSelectedMsgId] = useState<string>('msg_01');

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const suggestedPrompts = [
    'Show top 5 customers by revenue and net profit',
    'Why did Average Order Value (AOV) drop last week?',
    'Forecast Q4 inventory stockout risk on Wireless Headphones',
    'Compare regional sales performance against quarterly targets',
  ];

  const handleSend = async (promptText?: string) => {
    const textToSend = promptText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: `msg_u_${Date.now()}`,
      sender: 'USER',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!promptText) setInput('');
    setIsLoading(true);

    // Simulate SSE Streaming Response
    await new Promise((r) => setTimeout(r, 800));

    const aiMsgId = `msg_ai_${Date.now()}`;
    const aiResponse: ChatMessage = {
      id: aiMsgId,
      sender: 'AI',
      text: `Based on your PostgreSQL connection and confirmed semantic mappings, here is the analytical breakdown for: "${textToSend}". I evaluated 15,420 transaction records across the last 90 days.`,
      timestamp: new Date().toLocaleTimeString(),
      chart: {
        title: 'Revenue & Net Profit Attribution',
        type: 'bar',
        data: [
          { name: 'Acme Corp', value: 48500 },
          { name: 'Global Tech', value: 42100 },
          { name: 'Starlight Retail', value: 38900 },
          { name: 'Nexus Solutions', value: 31200 },
          { name: 'Vanguard Group', value: 29800 },
        ],
      },
      table: {
        columns: [
          { key: 'customer', header: 'Customer Account' },
          { key: 'orders', header: 'Total Orders' },
          { key: 'revenue', header: 'Gross Revenue' },
          { key: 'margin', header: 'Net Profit Margin' },
        ],
        rows: [
          { customer: 'Acme Corp', orders: 42, revenue: '$48,500.00', margin: '26.4%' },
          { customer: 'Global Tech', orders: 38, revenue: '$42,100.00', margin: '24.1%' },
          { customer: 'Starlight Retail', orders: 35, revenue: '$38,900.00', margin: '28.5%' },
          { customer: 'Nexus Solutions', orders: 29, revenue: '$31,200.00', margin: '22.0%' },
          { customer: 'Vanguard Group', orders: 25, revenue: '$29,800.00', margin: '25.8%' },
        ],
      },
      reasoningTrail: {
        businessRules: ['High Customer Value Threshold > $10,000 active', 'Zero Null Rate Verification verified'],
        semanticMapping: 'Mapped domain KPI `Total Gross Revenue` to physical column `orders.total_amount` (SUM).',
        sqlQuery: 'SELECT c.company_name AS customer, COUNT(o.id) AS orders, SUM(o.total_amount) AS revenue FROM orders o JOIN customers c ON o.customer_id = c.id GROUP BY c.company_name ORDER BY revenue DESC LIMIT 5;',
        confidence: 99,
        summary: 'Revenue attribution shows top 5 B2B clients generate 38.4% of total Q3 gross billings with healthy profit margins above 22%.',
      },
    };

    setMessages((prev) => [...prev, aiResponse]);
    setIsLoading(false);
  };

  const handleAddChartToDashboard = () => {
    toast.success('Widget Added', 'Visualization added to your Executive Dashboard workspace.');
  };

  return (
    <div className="flex flex-col h-[calc(100vh-10rem)] max-w-7xl mx-auto space-y-4 animate-in fade-in-50 duration-300">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-border shrink-0">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="purple">Backend V3: Natural Language Co-Pilot</Badge>
            <DomainSelector />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">AI Assistant & Analytics Chat</h1>
          <p className="text-sm text-muted-foreground">
            Ask complex business questions in natural language. Powered by real-time SQL generation and semantic reasoning trails.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setMessages([messages[0]]);
              toast.info('Chat Cleared', 'Started a fresh conversational session.');
            }}
            leftIcon={<RefreshCw className="w-3.5 h-3.5" />}
          >
            Reset Session
          </Button>
        </div>
      </div>

      {/* Suggested Prompts Bar */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 shrink-0">
        <span className="text-xs font-semibold text-muted-foreground whitespace-nowrap flex items-center gap-1">
          <Sparkles className="w-3.5 h-3.5 text-purple-500" />
          Suggested:
        </span>
        {suggestedPrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-full bg-card hover:bg-primary/10 border border-border hover:border-primary text-xs text-foreground font-medium whitespace-nowrap transition-all shadow-sm disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-6 p-4 rounded-2xl bg-muted/20 border border-border">
        {messages.map((msg) => {
          const isUser = msg.sender === 'USER';
          return (
            <div key={msg.id} className={`flex items-start gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
              <div
                className={`w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-md ${
                  isUser ? 'bg-primary text-primary-foreground' : 'bg-purple-600 text-white'
                }`}
              >
                {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              <div className={`space-y-3 max-w-4xl w-full ${isUser ? 'text-right' : 'text-left'}`}>
                <div className="flex items-center gap-2 px-1">
                  <span className="text-xs font-bold text-foreground">{isUser ? 'You' : 'BusinessLens AI Co-Pilot'}</span>
                  <span className="text-[10px] text-muted-foreground font-mono">{msg.timestamp}</span>
                </div>

                {/* Bubble */}
                <div
                  className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-sm ${
                    isUser
                      ? 'bg-primary text-primary-foreground rounded-tr-none inline-block text-left'
                      : 'bg-card border border-border text-foreground rounded-tl-none space-y-4'
                  }`}
                >
                  <p>{msg.text}</p>

                  {/* AI Embedded Table */}
                  {msg.table && (
                    <div className="pt-2 border-t border-border/80">
                      <div className="flex items-center justify-between pb-2">
                        <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                          <TableIcon className="w-3.5 h-3.5 text-primary" />
                          Tabular Response Data
                        </span>
                        <Button variant="ghost" size="sm" onClick={() => toast.success('CSV Exported', 'Table data downloaded.')} className="h-6 text-[10px]">
                          Export CSV
                        </Button>
                      </div>
                      <div className="bg-background rounded-xl border border-border overflow-hidden">
                        <DataTable data={msg.table.rows} columns={msg.table.columns} pageSize={5} />
                      </div>
                    </div>
                  )}

                  {/* AI Embedded Chart */}
                  {msg.chart && (
                    <div className="pt-2 border-t border-border/80">
                      <div className="flex items-center justify-between pb-2">
                        <span className="text-xs font-bold text-foreground flex items-center gap-1.5">
                          <BarChart3 className="w-3.5 h-3.5 text-purple-500" />
                          {msg.chart.title}
                        </span>
                        <Button variant="outline" size="sm" onClick={handleAddChartToDashboard} leftIcon={<Plus className="w-3 h-3" />} className="h-6 text-[10px]">
                          Add to Dashboard
                        </Button>
                      </div>
                      <div className="bg-background rounded-xl border border-border p-3">
                        <ChartWrapper
                          title={msg.chart.title}
                          options={{
                            tooltip: { trigger: 'axis' },
                            grid: { left: '3%', right: '4%', bottom: '5%', containLabel: true },
                            xAxis: { type: 'category', data: msg.chart.data.map((d) => d.name) },
                            yAxis: { type: 'value', axisLabel: { formatter: '${value}' } },
                            series: [{ type: 'bar', barWidth: 28, itemStyle: { color: '#8b5cf6', borderRadius: [4, 4, 0, 0] }, data: msg.chart.data.map((d) => d.value) }],
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Expanded Reasoning Trail (Backend V3) */}
                  {msg.reasoningTrail && (
                    <div className="p-3.5 rounded-xl bg-purple-500/[0.04] border border-purple-500/20 space-y-2.5 text-xs text-left">
                      <div className="flex items-center justify-between border-b border-purple-500/20 pb-2">
                        <span className="font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1.5">
                          <Sparkles className="w-4 h-4" />
                          Expanded Reasoning Trail & Lineage
                        </span>
                        <Badge variant="success" size="sm">
                          {msg.reasoningTrail.confidence}% Confidence
                        </Badge>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                        <div className="space-y-1">
                          <span className="text-muted-foreground font-semibold flex items-center gap-1">
                            <Layers className="w-3 h-3 text-primary" /> Semantic Lineage:
                          </span>
                          <p className="text-foreground font-medium">{msg.reasoningTrail.semanticMapping}</p>
                        </div>
                        <div className="space-y-1">
                          <span className="text-muted-foreground font-semibold flex items-center gap-1">
                            <ShieldCheck className="w-3 h-3 text-emerald-500" /> Business Rules Verified:
                          </span>
                          <p className="text-foreground font-medium">{msg.reasoningTrail.businessRules.join(' • ')}</p>
                        </div>
                      </div>

                      <div className="space-y-1 pt-1">
                        <span className="text-muted-foreground font-semibold text-[11px] flex items-center gap-1">
                          <Database className="w-3 h-3 text-blue-500" /> Executed PostgreSQL Query:
                        </span>
                        <div className="p-2 rounded bg-slate-950 border border-slate-800 font-mono text-[10px] text-emerald-400 overflow-x-auto">
                          {msg.reasoningTrail.sqlQuery}
                        </div>
                      </div>

                      <div className="pt-2 border-t border-purple-500/20 flex items-center justify-between">
                        <span className="text-[11px] text-muted-foreground">{msg.reasoningTrail.summary}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedMsgId(msg.id);
                            setExplainModalOpen(true);
                          }}
                          className="h-6 text-[10px] text-purple-600 dark:text-purple-400 font-bold shrink-0"
                        >
                          Full Audit Report &rarr;
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex items-center gap-3 text-xs text-muted-foreground animate-pulse p-4">
            <Bot className="w-5 h-5 text-purple-500" />
            <span>BusinessLens AI is synthesizing SQL query results and reasoning trail...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="flex items-center gap-3 p-3 rounded-2xl bg-card border border-border shadow-md shrink-0">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question about revenue, profit margins, inventory risks, or customer cohorts..."
          className="flex-1 bg-transparent text-xs sm:text-sm text-foreground focus:outline-none px-2"
          disabled={isLoading}
        />
        <Button
          variant="primary"
          size="md"
          onClick={() => handleSend()}
          disabled={!input.trim() || isLoading}
          isLoading={isLoading}
          rightIcon={<Send className="w-4 h-4" />}
          className="font-bold shrink-0"
        >
          Send
        </Button>
      </div>

      {/* Universal Explainability Panel */}
      <ExplainabilityPanel
        isOpen={explainModalOpen}
        onClose={() => setExplainModalOpen(false)}
        targetId="ai_query_9482"
        targetType="KPI"
        title="AI Assistant Natural Language Synthesis Trail"
      />
    </div>
  );
};
