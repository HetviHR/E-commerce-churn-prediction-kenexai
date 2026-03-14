import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import {
  Users, Star, Filter, ChevronDown, MessageSquare, ArrowUpRight,
  Brain, Loader2, WifiOff, ShieldAlert, TrendingUp
} from 'lucide-react';
import KPICard from '../components/KPICard';
import { DEMO_CUSTOMER } from '../api/client';
import { usePrediction } from '../api/usePrediction';

const customerData = [
  { id: 'CUST-8924', city: 'New York', risk: 'High Risk', inactiveDays: 45, complaints: 2, satisfaction: 2.4 },
  { id: 'CUST-7211', city: 'London', risk: 'High Risk', inactiveDays: 32, complaints: 1, satisfaction: 3.1 },
  { id: 'CUST-4490', city: 'San Francisco', risk: 'Medium Risk', inactiveDays: 18, complaints: 0, satisfaction: 3.8 },
  { id: 'CUST-3182', city: 'Berlin', risk: 'Low Risk', inactiveDays: 4, complaints: 0, satisfaction: 4.9 },
  { id: 'CUST-9012', city: 'Toronto', risk: 'Medium Risk', inactiveDays: 21, complaints: 3, satisfaction: 2.8 },
  { id: 'CUST-5543', city: 'Sydney', risk: 'High Risk', inactiveDays: 60, complaints: 4, satisfaction: 1.5 },
];

// Colour-code churn probability
function probColor(prob) {
  if (prob >= 0.7) return { text: 'text-red-400', bg: 'bg-red-500', label: 'High Risk' };
  if (prob >= 0.3) return { text: 'text-amber-400', bg: 'bg-amber-500', label: 'Medium Risk' };
  return { text: 'text-emerald-400', bg: 'bg-emerald-500', label: 'Low Risk' };
}

const PERSONA_COLORS = {
  'High Churn Risk': 'text-red-400 bg-red-500/10 border-red-500/30',
  'Discount Seekers': 'text-amber-400 bg-amber-500/10 border-amber-500/30',
  'Loyal Customers': 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
  'Premium Customers': 'text-violet-400 bg-violet-500/10 border-violet-500/30',
};

export default function CustomerSuccess() {
  const { prediction, loading, error } = usePrediction(DEMO_CUSTOMER);
  const colors = prediction ? probColor(prediction.churn_probability) : null;
  const personaCls = prediction
    ? (PERSONA_COLORS[prediction.persona] ?? 'text-gray-400 bg-gray-500/10 border-gray-500/30')
    : '';

  return (
    <div className="w-full text-white animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="text-gray-400 text-sm mb-1">Customer Success</p>
          <h1 className="text-3xl font-bold tracking-tight">Retention Dashboard</h1>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard title="Needs Contact" value="142" subtitle="↗ 14 Increased" color="orange" />
        <KPICard title="Avg Satisfaction" value="3.8 / 5" subtitle="↘ 0.2 Decreased" color="teal" />
        <KPICard title="Open Complaints" value="24" subtitle="↘ 8 Decreased" color="blue" />
        <KPICard title="Resolved (Week)" value="186" subtitle="↗ 45 Handled" color="purple" />
      </div>

      {/* ── LIVE: ML Prediction Card ── */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#6366F1]/20 mb-6 relative overflow-hidden">
        <div className="absolute -top-20 -right-20 w-72 h-72 bg-[#6366F1]/8 rounded-full blur-[100px] pointer-events-none" />
        <div className="flex justify-between items-center mb-6 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#6366F1]/20 flex items-center justify-center shrink-0">
              <Brain size={18} className="text-[#6366F1]" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-200">Live ML Prediction</h3>
              <p className="text-xs text-gray-500">Demo customer · /predict/full endpoint</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#6366F1]/10 text-[#6366F1] rounded-full text-xs font-semibold border border-[#6366F1]/20">
            ● Live
          </span>
        </div>

        {loading && (
          <div className="flex items-center justify-center gap-3 py-8 text-gray-400 relative z-10">
            <Loader2 size={20} className="animate-spin text-[#6366F1]" />
            <span className="text-sm">Running ML inference...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-3 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm relative z-10">
            <WifiOff size={16} />
            <span>ML backend offline — {error}</span>
          </div>
        )}

        {!loading && !error && prediction && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">

            {/* Churn probability */}
            <div className="bg-[#1A1D27] rounded-2xl p-5 border border-[#2A2D39]">
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                <ShieldAlert size={12} /> Churn Probability
              </p>
              <div className="flex items-end gap-2 mb-3">
                <span className={`text-4xl font-black ${colors.text}`}>
                  {Math.round(prediction.churn_probability * 100)}%
                </span>
                <span className={`text-sm font-semibold mb-1 ${colors.text}`}>
                  {prediction.churn_prediction === 1 ? '→ Will Churn' : '→ Will Retain'}
                </span>
              </div>
              <div className="w-full bg-[#2A2D39] rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-700 ${colors.bg}`}
                  style={{ width: `${Math.round(prediction.churn_probability * 100)}%` }}
                />
              </div>
            </div>

            {/* Persona + Cluster */}
            <div className="bg-[#1A1D27] rounded-2xl p-5 border border-[#2A2D39]">
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-3">Customer Segment</p>
              <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold border mb-3 ${personaCls}`}>
                {prediction.persona}
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Cluster <span className="text-gray-300 font-bold">#{prediction.cluster}</span> · KMeans segmentation
              </p>
            </div>

            {/* Top factors */}
            <div className="bg-[#1A1D27] rounded-2xl p-5 border border-[#2A2D39]">
              <p className="text-xs text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1.5">
                <TrendingUp size={12} /> Top Churn Factors
              </p>
              <ol className="space-y-2">
                {prediction.top_factors.map((f, i) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <span className="w-5 h-5 rounded-full bg-[#6366F1]/20 text-[#6366F1] text-[10px] font-bold flex items-center justify-center shrink-0">
                      {i + 1}
                    </span>
                    <span className="text-gray-200 font-medium">{f}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        )}
      </div>

      {/* Existing At-Risk table */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">

        {/* Filter Bar */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
              <Filter size={18} className="text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">At-Risk Customers</h3>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1A1D27] hover:bg-[#2A2D39] transition-colors rounded-full text-sm font-medium text-gray-300 border border-[#2A2D39]">
              Risk Level: All <ChevronDown size={14} />
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1A1D27] hover:bg-[#2A2D39] transition-colors rounded-full text-sm font-medium text-gray-300 border border-[#2A2D39]">
              City: All <ChevronDown size={14} />
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-[#1A1D27] hover:bg-[#2A2D39] transition-colors rounded-full text-sm font-medium text-gray-300 border border-[#2A2D39]">
              Category: All <ChevronDown size={14} />
            </button>
            <button className="w-9 h-9 bg-[#6366F1] rounded-full flex items-center justify-center text-white hover:bg-[#4f46e5]">
              <ArrowUpRight size={16} />
            </button>
          </div>
        </div>

        {/* Customer Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-[11px] text-gray-500 uppercase tracking-wider border-b border-[#2A2D39]">
              <tr>
                <th className="px-4 py-3 font-medium">Customer ID</th>
                <th className="px-4 py-3 font-medium">City</th>
                <th className="px-4 py-3 font-medium">Risk Level</th>
                <th className="px-4 py-3 font-medium">Days Inactive</th>
                <th className="px-4 py-3 font-medium">Complaints</th>
                <th className="px-4 py-3 font-medium">Satisfaction</th>
                <th className="px-4 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {customerData.map((row, i) => (
                <tr key={i} className="border-b border-[#1A1D27] hover:bg-[#1A1D27]/50 transition-colors group">
                  <td className="px-4 py-4 font-semibold text-gray-200">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
                        <Users size={14} className="text-gray-400" />
                      </div>
                      {row.id}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-gray-400 font-medium">{row.city}</td>
                  <td className="px-4 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${row.risk === 'High Risk' ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' :
                        row.risk === 'Medium Risk' ? 'bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20' :
                          'bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/20'
                      }`}>
                      {row.risk}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-gray-300">
                    <span className={row.inactiveDays > 30 ? 'text-red-400 font-semibold' : ''}>
                      {row.inactiveDays} days
                    </span>
                  </td>
                  <td className="px-4 py-4 text-gray-300">
                    <span className={row.complaints > 0 ? 'text-orange-400 font-semibold' : ''}>
                      {row.complaints} open
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <div className="flex items-center gap-1">
                      <Star size={14} className={row.satisfaction < 3.0 ? 'text-red-400 fill-red-400' : 'text-yellow-400 fill-yellow-400'} />
                      <span className={row.satisfaction < 3.0 ? 'text-red-400 font-semibold' : 'text-gray-300'}>{row.satisfaction}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-right">
                    <button className="inline-flex items-center gap-2 px-4 py-2 bg-[#6366F1]/10 hover:bg-[#6366F1]/20 text-[#6366F1] transition-colors rounded-full text-xs font-semibold uppercase tracking-wide border border-[#6366F1]/20 group-hover:border-[#6366F1]/50">
                      <MessageSquare size={14} /> Contact
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Complaints by Category Chart */}
      <div className="mt-6 bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
            <MessageSquare size={18} className="text-orange-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-200">Complaints by Category</h3>
        </div>
        <div className="h-[220px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={[
                { category: 'Delivery', count: 142 },
                { category: 'Product Quality', count: 89 },
                { category: 'Payment Issues', count: 67 },
                { category: 'Customer Support', count: 54 },
              ]}
              layout="vertical"
              margin={{ top: 0, right: 20, bottom: 0, left: 20 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#2A2D39" horizontal={false} />
              <XAxis type="number" stroke="#6B7280" tick={{ fill: '#6B7280', fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="category" width={130} stroke="#6B7280" tick={{ fill: '#E5E7EB', fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: '#1A1D27' }}
                contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                itemStyle={{ color: '#F97316' }}
                formatter={(value) => [`${value} complaints`, 'Count']}
              />
              <Bar dataKey="count" fill="#F97316" radius={[0, 6, 6, 0]} barSize={22} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
}
