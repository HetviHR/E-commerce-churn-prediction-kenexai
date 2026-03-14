import React from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';
import { Users, ArrowUpRight, TrendingUp, Loader2, WifiOff } from 'lucide-react';
import KPICard from '../components/KPICard';
import { useFeatureImportance } from '../api/usePrediction';

const churnByCategoryData = [
  { category: 'Electronics', churn: 12.4 },
  { category: 'Clothing', churn: 8.2 },
  { category: 'Home & Garden', churn: 15.6 },
  { category: 'Sports', churn: 6.8 },
  { category: 'Toys', churn: 4.1 },
];

const monthlyChurnTrendData = [
  { month: 'Sep', rate: 4.2 },
  { month: 'Oct', rate: 4.5 },
  { month: 'Nov', rate: 5.1 },
  { month: 'Dec', rate: 6.8 },
  { month: 'Jan', rate: 5.4 },
  { month: 'Feb', rate: 4.8 },
];

const riskLevelData = [
  { name: 'Low Risk', value: 65, color: '#10B981' },
  { name: 'Medium Risk', value: 25, color: '#F59E0B' },
  { name: 'High Risk', value: 10, color: '#EF4444' },
];

// Build recharts bar data from the feature importance API response, top 8
function toBarData(importanceMap) {
  return Object.entries(importanceMap)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
    .map(([feature, value]) => ({ feature, value: parseFloat((value * 100).toFixed(2)) }));
}

const ML_BAR_COLOR = '#6366F1';

export default function Marketing() {
  const { data: importanceMap, loading: impLoading, error: impError } = useFeatureImportance();
  const mlBarData = toBarData(importanceMap);

  return (
    <div className="w-full text-white animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="text-gray-400 text-sm mb-1">Marketing</p>
          <h1 className="text-3xl font-bold tracking-tight">Manager Dashboard</h1>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard title="Churn Rate" value="4.8%" subtitle="↗ 1.2% Increased" color="orange" />
        <KPICard title="Revenue at Risk" value="$142.5K" subtitle="↗ $12.5K Increased" color="teal" />
        <KPICard title="Avg CLV" value="$1,240" subtitle="↗ $45 Increased" color="blue" />
        <KPICard title="Active Customers" value="12,450" subtitle="↗ 1,240 New" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Bar Chart: Churn by Category */}
        <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
          <div className="flex justify-between items-center mb-10">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-200">Churn by Category</h3>
            </div>
            <button className="w-9 h-9 bg-[#2A2D39] rounded-full flex items-center justify-center text-white hover:bg-[#3A3D49]">
              <ArrowUpRight size={16} />
            </button>
          </div>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={churnByCategoryData} layout="vertical" margin={{ top: 0, right: 0, bottom: 0, left: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2D39" horizontal={true} vertical={false} />
                <XAxis type="number" stroke="#6B7280" tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} />
                <YAxis type="category" dataKey="category" stroke="#6B7280" tick={{ fill: '#E5E7EB' }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#1A1D27' }}
                  contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                />
                <Bar dataKey="churn" fill="#6366F1" radius={[0, 4, 4, 0]} barSize={20} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Line Chart: Churn Trend */}
        <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
          <div className="flex justify-between items-center mb-10">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-200">Monthly Churn Trend</h3>
            </div>
            <button className="px-4 py-2 bg-[#1A1D27] hover:bg-[#2A2D39] transition-colors rounded-full text-sm font-medium text-gray-300 border border-[#2A2D39]">
              6 Months v
            </button>
          </div>
          <div className="h-[250px] w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthlyChurnTrendData}>
                <defs>
                  <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#F59E0B" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2D39" vertical={false} />
                <XAxis dataKey="month" stroke="#6B7280" tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} dy={10} />
                <YAxis stroke="#6B7280" tick={{ fill: '#6B7280' }} axisLine={false} tickLine={false} dx={-10} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                  itemStyle={{ color: '#F59E0B' }}
                />
                <Line
                  type="monotone" dataKey="rate" stroke="#F59E0B" strokeWidth={4}
                  dot={{ r: 4, fill: '#13151D', stroke: '#F59E0B', strokeWidth: 2 }}
                  activeDot={{ r: 6, fill: '#F59E0B', stroke: '#13151D', strokeWidth: 3 }}
                  style={{ filter: 'drop-shadow(0px 8px 12px rgba(245, 158, 11, 0.3))' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Pie Chart: Risk Level Distribution */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230] relative overflow-hidden lg:w-1/2 mb-6">
        <div className="flex justify-between items-center mb-8 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
              <Users size={18} className="text-gray-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-200">Customer Risk Distribution</h3>
          </div>
          <button className="w-9 h-9 bg-[#6366F1] rounded-full flex items-center justify-center text-white hover:bg-[#4f46e5]">
            <ArrowUpRight size={16} />
          </button>
        </div>

        <div className="h-[250px] w-full flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={riskLevelData} cx="50%" cy="50%" innerRadius={60} outerRadius={90}
                paddingAngle={5} dataKey="value" stroke="none">
                {riskLevelData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Legend verticalAlign="middle" align="right" layout="vertical"
                iconType="circle" wrapperStyle={{ paddingLeft: '20px' }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── LIVE: ML Churn Drivers bar chart ── */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#6366F1]/20 mb-6 relative overflow-hidden">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-[#6366F1]/8 rounded-full blur-[80px] pointer-events-none" />
        <div className="flex justify-between items-center mb-8 relative z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-[#6366F1]/20 flex items-center justify-center shrink-0">
              <TrendingUp size={18} className="text-[#6366F1]" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-200">ML Churn Drivers</h3>
              <p className="text-xs text-gray-500">Live · RandomForest feature importance · relative % score</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#6366F1]/10 text-[#6366F1] rounded-full text-xs font-semibold border border-[#6366F1]/20">
            ● Live
          </span>
        </div>

        {impLoading && (
          <div className="flex items-center justify-center gap-3 py-10 text-gray-400 relative z-10">
            <Loader2 size={20} className="animate-spin text-[#6366F1]" />
            <span className="text-sm">Loading ML feature importance...</span>
          </div>
        )}

        {impError && (
          <div className="flex items-center gap-3 px-4 py-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm relative z-10">
            <WifiOff size={16} />
            <span>ML backend offline — {impError}</span>
          </div>
        )}

        {!impLoading && !impError && mlBarData.length > 0 && (
          <div className="h-[280px] w-full relative z-10">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mlBarData} layout="vertical" margin={{ top: 0, right: 30, bottom: 0, left: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2D39" horizontal={false} />
                <XAxis type="number" stroke="#6B7280" tick={{ fill: '#6B7280', fontSize: 11 }}
                  axisLine={false} tickLine={false} unit="%" />
                <YAxis type="category" dataKey="feature" width={160} stroke="#6B7280"
                  tick={{ fill: '#E5E7EB', fontSize: 12 }} axisLine={false} tickLine={false} />
                <Tooltip
                  cursor={{ fill: '#1A1D27' }}
                  contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                  itemStyle={{ color: ML_BAR_COLOR }}
                  formatter={(v) => [`${v}%`, 'Importance']}
                />
                <Bar dataKey="value" fill={ML_BAR_COLOR} radius={[0, 6, 6, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Top Cities by Churn Rate */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
            <Users size={18} className="text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-200">Top Cities by Churn Rate</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <thead className="text-[11px] text-gray-500 uppercase tracking-wider border-b border-[#2A2D39]">
              <tr>
                <th className="px-4 py-3 font-medium">City</th>
                <th className="px-4 py-3 font-medium">Churn Rate</th>
                <th className="px-4 py-3 font-medium">Revenue Impact</th>
                <th className="px-4 py-3 font-medium text-right">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {[
                { city: 'Mumbai', churn: '34%', revenue: '$18,200', risk: 'High Risk', color: 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20' },
                { city: 'Delhi', churn: '28%', revenue: '$14,500', risk: 'High Risk', color: 'text-[#EF4444] bg-[#EF4444]/10 border-[#EF4444]/20' },
                { city: 'Bangalore', churn: '22%', revenue: '$11,800', risk: 'Medium Risk', color: 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20' },
                { city: 'Chennai', churn: '18%', revenue: '$9,200', risk: 'Medium Risk', color: 'text-[#F59E0B] bg-[#F59E0B]/10 border-[#F59E0B]/20' },
                { city: 'Pune', churn: '12%', revenue: '$6,400', risk: 'Low Risk', color: 'text-[#10B981] bg-[#10B981]/10 border-[#10B981]/20' },
              ].map((row, i) => (
                <tr key={i} className="border-b border-[#1A1D27] hover:bg-[#1A1D27]/50 transition-colors group">
                  <td className="px-4 py-4 font-semibold text-gray-200">{row.city}</td>
                  <td className="px-4 py-4 text-gray-300 font-mono font-medium">{row.churn}</td>
                  <td className="px-4 py-4 text-gray-300 font-medium">{row.revenue}</td>
                  <td className="px-4 py-4 text-right">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${row.color}`}>
                      {row.risk}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
