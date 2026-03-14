import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  AlertTriangle, ArrowUpRight, Sparkles, MessageSquare, Check,
  ChevronDown, Send, Loader2, WifiOff
} from 'lucide-react';
import KPICard from '../components/KPICard';
import { predictFull } from '../api/client';

// Static demo customer rows — churn score used as display-only UI metric
const atRiskCustomers = [
  {
    id: 'CUST-8924', city: 'New York', score: 92, inactiveDays: 45, complaints: 2,
    features: {
      Tenure: 3, PreferredLoginDevice: 'Mobile Phone', CityTier: 1, WarehouseToHome: 25,
      PreferredPaymentMode: 'Debit Card', Gender: 'Male', HourSpendOnApp: 0.5,
      NumberOfDeviceRegistered: 2, PreferedOrderCat: 'Mobile', SatisfactionScore: 1,
      MaritalStatus: 'Single', NumberOfAddress: 2, Complain: 1,
      OrderAmountHikeFromlastYear: 10, CouponUsed: 6, OrderCount: 1, DaySinceLastOrder: 45, CashbackAmount: 30
    }
  },
  {
    id: 'CUST-7211', city: 'London', score: 88, inactiveDays: 32, complaints: 1,
    features: {
      Tenure: 6, PreferredLoginDevice: 'Mobile Phone', CityTier: 2, WarehouseToHome: 20,
      PreferredPaymentMode: 'Credit Card', Gender: 'Female', HourSpendOnApp: 1.0,
      NumberOfDeviceRegistered: 3, PreferedOrderCat: 'Fashion', SatisfactionScore: 2,
      MaritalStatus: 'Married', NumberOfAddress: 3, Complain: 1,
      OrderAmountHikeFromlastYear: 12, CouponUsed: 3, OrderCount: 2, DaySinceLastOrder: 32, CashbackAmount: 50
    }
  },
  {
    id: 'CUST-5543', city: 'Sydney', score: 85, inactiveDays: 60, complaints: 4,
    features: {
      Tenure: 2, PreferredLoginDevice: 'Computer', CityTier: 1, WarehouseToHome: 30,
      PreferredPaymentMode: 'COD', Gender: 'Male', HourSpendOnApp: 0.3,
      NumberOfDeviceRegistered: 2, PreferedOrderCat: 'Grocery', SatisfactionScore: 1,
      MaritalStatus: 'Divorced', NumberOfAddress: 1, Complain: 1,
      OrderAmountHikeFromlastYear: 5, CouponUsed: 8, OrderCount: 1, DaySinceLastOrder: 60, CashbackAmount: 20
    }
  },
  {
    id: 'CUST-9012', city: 'Toronto', score: 76, inactiveDays: 21, complaints: 3,
    features: {
      Tenure: 8, PreferredLoginDevice: 'Mobile Phone', CityTier: 2, WarehouseToHome: 15,
      PreferredPaymentMode: 'UPI', Gender: 'Female', HourSpendOnApp: 2.0,
      NumberOfDeviceRegistered: 4, PreferedOrderCat: 'Laptop & Accessory', SatisfactionScore: 2,
      MaritalStatus: 'Single', NumberOfAddress: 4, Complain: 1,
      OrderAmountHikeFromlastYear: 20, CouponUsed: 4, OrderCount: 4, DaySinceLastOrder: 21, CashbackAmount: 80
    }
  },
  {
    id: 'CUST-2231', city: 'Paris', score: 72, inactiveDays: 28, complaints: 0,
    features: {
      Tenure: 10, PreferredLoginDevice: 'Mobile Phone', CityTier: 3, WarehouseToHome: 12,
      PreferredPaymentMode: 'E wallet', Gender: 'Male', HourSpendOnApp: 2.5,
      NumberOfDeviceRegistered: 3, PreferedOrderCat: 'Fashion', SatisfactionScore: 3,
      MaritalStatus: 'Married', NumberOfAddress: 2, Complain: 0,
      OrderAmountHikeFromlastYear: 18, CouponUsed: 2, OrderCount: 6, DaySinceLastOrder: 28, CashbackAmount: 120
    }
  },
];

const sampleChatMessages = [
  { role: 'user', text: "Which customers haven't ordered in 60 days?" },
  { role: 'ai', text: 'There are 234 customers inactive for 60+ days. Highest risk are in Mumbai and Delhi.' },
];

const RISK_BAR_COLORS = [
  { from: '#FF8A8A', to: '#EF4444' },
  { from: '#FFB970', to: '#F59E0B' },
  { from: '#A898FF', to: '#6366F1' },
];

export default function AIRetention() {
  const [selectedCustomer, setSelectedCustomer] = useState(atRiskCustomers[0]);
  const [messageChannel, setMessageChannel] = useState('Email');
  const [messagesSent, setMessagesSent] = useState(156);
  const [sentFlash, setSentFlash] = useState(false);
  const [chatMessages, setChatMessages] = useState(sampleChatMessages);
  const [chatInput, setChatInput] = useState('');

  // ── Live prediction state ──────────────────────────────────────────────
  const [prediction, setPrediction] = useState(null);
  const [predLoading, setPredLoading] = useState(true);
  const [predError, setPredError] = useState(null);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Fetch prediction whenever selected customer changes
  const fetchPrediction = useCallback(async (customer) => {
    setPredLoading(true);
    setPredError(null);
    setPrediction(null);
    try {
      const result = await predictFull(customer.features);
      setPrediction(result);
    } catch (err) {
      setPredError(err.message ?? 'Backend offline.');
    } finally {
      setPredLoading(false);
    }
  }, []);

  useEffect(() => { fetchPrediction(selectedCustomer); }, [selectedCustomer, fetchPrediction]);

  const handleMarkAsSent = () => {
    setMessagesSent(prev => prev + 1);
    setSentFlash(true);
    setTimeout(() => setSentFlash(false), 2000);
  };

  const handleSendChat = () => {
    const trimmed = chatInput.trim();
    if (!trimmed) return;
    setChatMessages(prev => [
      ...prev,
      { role: 'user', text: trimmed },
      { role: 'ai', text: `Analyzing your question about "${trimmed}"... Based on current data, I suggest focusing on customers inactive for 30+ days with at least 1 complaint. Would you like me to generate a retention message for them?` }
    ]);
    setChatInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendChat(); }
  };

  // Build retention message from API or fall back to static template
  const retentionMessage = prediction?.retention_strategy?.retention_message
    ?? `Hi there,\n\nWe noticed you haven't visited us in ${selectedCustomer.inactiveDays} days. We've put together a special personalized offer. Use code COMEBACK20 for 20% off your next order.`;

  // Build risk factor bars from API top_factors or fall back to static
  const riskBars = prediction?.top_factors
    ? prediction.top_factors.slice(0, 3).map((f, i) => ({ label: f, pct: 85 - i * 20 }))
    : [
      { label: 'Inactivity', pct: 85 },
      { label: 'Complaints', pct: 60 },
      { label: 'Low Order Value', pct: 40 },
    ];

  return (
    <div className="w-full text-white animate-in fade-in duration-500 pb-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="text-gray-400 text-sm mb-1">AI Retention</p>
          <h1 className="text-3xl font-bold tracking-tight">AI Retention Panel</h1>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard title="At-Risk Customers" value="428" subtitle="↗ 12 Increased" color="orange" />
        <KPICard title="Messages Sent Today" value={String(messagesSent)} subtitle={`↗ ${messagesSent - 111} Vs Yesterday`} color="blue" />
        <KPICard
          title="Avg Churn Score"
          value={prediction ? `${Math.round(prediction.churn_probability * 100)}%` : '—'}
          subtitle={prediction ? `← Live · ${prediction.persona}` : 'Loading...'}
          color="teal"
        />
        <KPICard title="Retention Rate" value="32.5%" subtitle="↗ 4.1% Increased" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Left Column: Customer List */}
        <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230] flex flex-col h-full">
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
                <AlertTriangle size={18} className="text-orange-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-200">Critical Risk Customers</h3>
            </div>
            <button className="w-9 h-9 bg-[#2A2D39] rounded-full flex items-center justify-center text-white hover:bg-[#3A3D49]">
              <ArrowUpRight size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-[11px] text-gray-500 uppercase tracking-wider border-b border-[#2A2D39]">
                <tr>
                  <th className="px-2 py-3 font-medium">Customer ID</th>
                  <th className="px-2 py-3 font-medium">Churn Score</th>
                  <th className="px-2 py-3 font-medium">Inactive/Complaints</th>
                  <th className="px-2 py-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {atRiskCustomers.map((row, i) => (
                  <tr key={i}
                    onClick={() => setSelectedCustomer(row)}
                    className={`border-b border-[#1A1D27] hover:bg-[#1A1D27]/80 transition-colors cursor-pointer group ${selectedCustomer.id === row.id ? 'bg-[#1A1D27]' : ''}`}>
                    <td className="px-2 py-4 font-semibold text-gray-200">
                      <div className="flex flex-col">
                        <span>{row.id}</span>
                        <span className="text-[11px] text-gray-500 font-normal">{row.city}</span>
                      </div>
                    </td>
                    <td className="px-2 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-[#2A2D39] rounded-full h-1.5 max-w-[60px]">
                          <div className={`h-1.5 rounded-full ${row.score > 85 ? 'bg-red-500' : 'bg-orange-500'}`} style={{ width: `${row.score}%` }}></div>
                        </div>
                        <span className={`font-semibold ${row.score > 85 ? 'text-red-400' : 'text-orange-400'}`}>{row.score}</span>
                      </div>
                    </td>
                    <td className="px-2 py-4 text-gray-400">
                      <div className="flex flex-col gap-1 text-[11px]">
                        <span className={row.inactiveDays > 30 ? 'text-red-300' : ''}>{row.inactiveDays} days inactive</span>
                        <span className={row.complaints > 0 ? 'text-orange-300' : ''}>{row.complaints} complaints</span>
                      </div>
                    </td>
                    <td className="px-2 py-4 text-right">
                      <button className={`inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors ${selectedCustomer.id === row.id ? 'bg-[#6366F1] text-white' : 'bg-[#2A2D39] text-gray-300 group-hover:bg-[#6366F1] group-hover:text-white'}`}>
                        <MessageSquare size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Column: AI Panel & Risk Factors */}
        <div className="flex flex-col gap-6">

          {/* AI Message Panel */}
          <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230] flex flex-col relative overflow-hidden">
            <div className="absolute -top-20 -right-20 w-64 h-64 bg-[#6366F1]/10 rounded-full blur-[80px] pointer-events-none"></div>

            <div className="flex justify-between items-center mb-6 relative z-10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-[#6366F1]/20 flex items-center justify-center shrink-0">
                  <Sparkles size={18} className="text-[#6366F1]" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-200">AI Retention Strategist</h3>
                  <p className="text-xs text-gray-400">
                    Targeting {selectedCustomer.id}
                    {prediction && (
                      <span className="ml-2 text-[#6366F1]">· {prediction.persona}</span>
                    )}
                  </p>
                </div>
              </div>
              {/* Urgency badge */}
              {prediction?.retention_strategy?.urgency_level && (
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${prediction.retention_strategy.urgency_level === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border-red-500/30' :
                    prediction.retention_strategy.urgency_level === 'HIGH' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
                      'bg-amber-500/10 text-amber-400 border-amber-500/30'
                  }`}>
                  {prediction.retention_strategy.urgency_level}
                </span>
              )}
            </div>

            <div className="relative z-10 space-y-4">
              {/* Channel Selector */}
              <div className="flex items-center justify-between bg-[#1A1D27] p-2 rounded-xl border border-[#2A2D39]">
                <span className="text-sm text-gray-400 pl-2 font-medium">Channel</span>
                <div className="relative">
                  <select
                    className="appearance-none bg-[#2A2D39] text-white text-sm font-semibold py-2 pl-4 pr-10 rounded-lg hover:bg-[#3A3D49] outline-none border border-transparent focus:border-[#6366F1]/50 cursor-pointer transition-colors"
                    value={messageChannel}
                    onChange={(e) => setMessageChannel(e.target.value)}
                  >
                    <option value="Email">Email</option>
                    <option value="WhatsApp">WhatsApp</option>
                    <option value="SMS">SMS</option>
                    <option value="Push">Push Notification</option>
                  </select>
                  <ChevronDown size={14} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
                </div>
              </div>

              {/* Message Area */}
              <div className="bg-[#0A0D14] border border-[#2A2D39] rounded-2xl p-4 min-h-[100px]">
                {predLoading ? (
                  <div className="flex items-center gap-2 text-gray-500 text-sm">
                    <Loader2 size={14} className="animate-spin text-[#6366F1]" />
                    Generating AI retention strategy...
                  </div>
                ) : predError ? (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <WifiOff size={14} /> Backend offline · showing template
                  </div>
                ) : null}
                <p className="text-sm text-gray-300 leading-relaxed font-mono mt-2 whitespace-pre-line">
                  {retentionMessage}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-2">
                <button className="flex-1 flex items-center justify-center gap-2 bg-[#6366F1] hover:bg-[#4f46e5] text-white py-3 px-4 rounded-xl font-semibold transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)] hover:shadow-[0_0_25px_rgba(99,102,241,0.5)]">
                  <Sparkles size={16} /> Generate with AI
                </button>
                <button
                  onClick={handleMarkAsSent}
                  className={`flex items-center justify-center gap-2 py-3 px-6 rounded-xl font-semibold transition-all border ${sentFlash
                      ? 'bg-green-500 border-green-500 text-white shadow-[0_0_20px_rgba(34,197,94,0.4)]'
                      : 'bg-[#1A1D27] hover:bg-green-500/10 text-gray-200 border-green-500/30 hover:border-green-500/60 hover:text-green-400'
                    }`}
                >
                  <Check size={16} className={sentFlash ? 'text-white' : 'text-green-400'} />
                  {sentFlash ? 'Sent!' : 'Mark as Sent'}
                </button>
              </div>
            </div>
          </div>

          {/* Progress Bars (Risk Factors) — driven by API top_factors */}
          <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-sm font-semibold text-gray-400 tracking-wide uppercase">Primary Risk Factors</h3>
              {prediction && (
                <span className="text-[10px] text-[#6366F1] font-medium uppercase tracking-wider">● Live from ML</span>
              )}
            </div>
            <div className="space-y-5">
              {riskBars.map(({ label, pct }, i) => (
                <div key={label}>
                  <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-200 font-medium">{label}</span>
                    <span style={{ color: RISK_BAR_COLORS[i]?.to ?? '#6366F1' }} className="font-bold">{pct}% Impact</span>
                  </div>
                  <div className="w-full bg-[#1A1D27] rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-700"
                      style={{
                        width: `${pct}%`,
                        background: `linear-gradient(to right, ${RISK_BAR_COLORS[i]?.from ?? '#A898FF'}, ${RISK_BAR_COLORS[i]?.to ?? '#6366F1'})`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>

      {/* Chat Section */}
      <div className="mt-6 bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230] relative overflow-hidden">
        <div className="absolute -bottom-20 -left-20 w-72 h-72 bg-[#6366F1]/10 rounded-full blur-[100px] pointer-events-none"></div>

        <div className="flex items-center gap-3 mb-6 relative z-10">
          <div className="w-10 h-10 rounded-full bg-[#6366F1]/20 flex items-center justify-center shrink-0">
            <Sparkles size={18} className="text-[#6366F1]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-200">Ask about your customers</h3>
            <p className="text-xs text-gray-400">Powered by AI · Context-aware</p>
          </div>
        </div>

        <div className="relative z-10 space-y-4 max-h-64 overflow-y-auto pr-1 mb-4">
          {chatMessages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                  ? 'bg-[#6366F1] text-white rounded-br-sm'
                  : 'bg-[#1A1D27] text-gray-300 border border-[#2A2D39] rounded-bl-sm'
                }`}>
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <div className="relative z-10 flex gap-3 items-center">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about at-risk customers..."
            className="flex-1 bg-[#1A1D27] border border-[#2A2D39] focus:border-[#6366F1]/60 text-white placeholder-gray-500 text-sm px-5 py-3.5 rounded-xl outline-none transition-colors"
          />
          <button
            onClick={handleSendChat}
            className="w-12 h-12 bg-[#6366F1] hover:bg-[#4f46e5] text-white rounded-xl flex items-center justify-center transition-all shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:shadow-[0_0_20px_rgba(99,102,241,0.5)] shrink-0"
          >
            <Send size={18} />
          </button>
        </div>
      </div>

    </div>
  );
}
