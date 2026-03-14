import React from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Database, AlertTriangle, Layers, ArrowUpRight } from 'lucide-react';
import KPICard from '../components/KPICard';

const rowCountData = [
  { day: 'Sun', count: 14500 },
  { day: 'Mon', count: 14800 },
  { day: 'Tue', count: 15200 },
  { day: 'Wed', count: 15100 },
  { day: 'Thu', count: 15500 },
  { day: 'Fri', count: 15900 },
  { day: 'Sat', count: 16200 },
];

const missingValuesData = [
  { column: 'customer_id', missing: '0.0%', status: 'Clean' },
  { column: 'session_duration', missing: '2.4%', status: 'Warning' },
  { column: 'cart_value', missing: '0.5%', status: 'Clean' },
  { column: 'last_login', missing: '0.0%', status: 'Clean' },
  { column: 'device_type', missing: '5.1%', status: 'Alert' },
];

const dataTypeData = [
  { column: 'customer_id', expected: 'UUID', actual: 'String', match: true },
  { column: 'session_duration', expected: 'Integer', actual: 'Integer', match: true },
  { column: 'cart_value', expected: 'Float', actual: 'Float', match: true },
  { column: 'last_login', expected: 'Timestamp', actual: 'String', match: false },
  { column: 'device_type', expected: 'Categorical', actual: 'String', match: false },
];

export default function DataQuality() {
  return (
    <div className="w-full text-white animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-8">
        <div>
          <p className="text-gray-400 text-sm mb-1">Overview</p>
          <h1 className="text-3xl font-bold tracking-tight">Data Quality</h1>
        </div>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard title="Total Records" value="48,294" subtitle="↗ 2.4% Increased" color="orange" />
        <KPICard title="Missing Values %" value="1.6%" subtitle="↘ 0.8% Decreased" color="blue" />
        <KPICard title="Duplicate Rows" value="34" subtitle="↘ 12 Decreased" color="teal" />
        <KPICard title="Last Updated" value="2m ago" subtitle="✓ Sync Active" color="purple" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Chart */}
        <div className="lg:col-span-2 bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
          <div className="flex justify-between items-center mb-10">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
                <Database size={18} className="text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-200">Row Count</h3>
            </div>
            <div className="flex items-center gap-2">
               <button className="px-4 py-2 bg-[#1A1D27] hover:bg-[#2A2D39] transition-colors rounded-full text-sm font-medium text-gray-300 border border-[#2A2D39]">
                  Last 7 Days v
               </button>
               <button className="w-9 h-9 bg-[#6366F1] rounded-full flex items-center justify-center text-white hover:bg-[#4f46e5] md:flex hidden">
                 <ArrowUpRight size={16} />
               </button>
            </div>
          </div>
          
          <div className="h-[280px] w-full mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rowCountData}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2D39" vertical={false} />
                <XAxis dataKey="day" stroke="#6B7280" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} dy={10} />
                <YAxis stroke="#6B7280" tick={{fill: '#6B7280'}} axisLine={false} tickLine={false} dx={-10} domain={['dataMin - 500', 'dataMax + 500']} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1A1D27', border: '1px solid #2A2D39', borderRadius: '12px', color: '#fff' }}
                  itemStyle={{ color: '#6366F1' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="count" 
                  stroke="#6366F1" 
                  strokeWidth={4}
                  dot={false}
                  activeDot={{ r: 6, fill: '#6366F1', stroke: '#13151D', strokeWidth: 3 }}
                  style={{ filter: 'drop-shadow(0px 8px 12px rgba(99, 102, 241, 0.4))' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Missing Values Table */}
        <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230]">
          <div className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-3">
               <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
                  <AlertTriangle size={18} className="text-gray-400" />
                </div>
              <h3 className="text-lg font-semibold text-gray-200">Missing Values</h3>
            </div>
            <button className="w-8 h-8 bg-[#2A2D39] hover:bg-[#3A3D49] rounded-full flex items-center justify-center text-white transition-colors">
              <ArrowUpRight size={14} />
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-[11px] text-gray-500 uppercase tracking-wider border-b border-[#2A2D39]">
                <tr>
                  <th className="px-1 py-3 font-medium">Column</th>
                  <th className="px-1 py-3 font-medium text-right">Missing</th>
                </tr>
              </thead>
              <tbody>
                {missingValuesData.map((row, i) => (
                  <tr key={i} className="border-b border-[#1A1D27] hover:bg-[#1A1D27]/50 transition-colors group">
                    <td className="px-1 py-4 font-medium text-gray-300 group-hover:text-white transition-colors">{row.column}</td>
                    <td className={`px-1 py-4 text-right font-semibold flex justify-end items-center gap-2 ${
                      row.status === 'Clean' ? 'text-green-400' : 
                      row.status === 'Warning' ? 'text-yellow-400' : 'text-red-400'
                    }`}>
                      {row.missing}
                      <ArrowUpRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Data Type Checker */}
      <div className="bg-[#13151D] rounded-[32px] p-8 border border-[#1e2230] relative overflow-hidden">
        <div className="flex justify-between items-center mb-8 relative z-10">
          <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
                <Layers size={18} className="text-gray-400" />
              </div>
            <h3 className="text-lg font-semibold text-gray-200">Data Type Validation</h3>
          </div>
          <div className="flex gap-2">
            <button className="w-10 h-10 bg-[#1A1D27] hover:bg-[#2A2D39] rounded-full flex items-center justify-center text-gray-400 transition-colors">
              <div className="w-4 h-4 rounded-full border-2 border-current"></div>
            </button>
            <button className="w-10 h-10 bg-[#6366F1] hover:bg-[#4f46e5] rounded-full flex items-center justify-center text-white transition-colors">
              <ArrowUpRight size={18} />
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto w-full relative z-10">
          <table className="w-full text-sm text-left">
             <thead className="text-[11px] text-gray-500 uppercase tracking-wider border-b border-[#2A2D39]">
                <tr>
                  <th className="px-4 py-3 font-medium">#</th>
                  <th className="px-4 py-3 font-medium">Column Name</th>
                  <th className="px-4 py-3 font-medium">Expected Type</th>
                  <th className="px-4 py-3 font-medium">Actual Type</th>
                  <th className="px-4 py-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {dataTypeData.map((row, i) => (
                  <tr key={i} className="border-b border-[#1A1D27] hover:bg-[#1A1D27]/50 transition-colors">
                    <td className="px-4 py-4 font-medium text-gray-500">
                      0{i+1}
                    </td>
                    <td className="px-4 py-4 font-medium text-gray-200">
                      {row.column}
                    </td>
                    <td className="px-4 py-4 text-gray-400">{row.expected}</td>
                    <td className="px-4 py-4 text-gray-300">{row.actual}</td>
                    <td className="px-4 py-4 text-right">
                      {row.match ? (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-500/10 text-green-400 rounded-full text-xs font-semibold uppercase tracking-wider">
                          Match
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-500/10 text-red-400 rounded-full text-xs font-semibold uppercase tracking-wider">
                          Mismatch
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
          </table>
        </div>
      </div>

      {/* Outlier Detection */}
      <div className="mt-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-[#1A1D27] flex items-center justify-center shrink-0">
            <AlertTriangle size={18} className="text-yellow-400" />
          </div>
          <h3 className="text-lg font-semibold text-gray-200">Outlier Detection</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* Card 1 - Red */}
          <div className="bg-[#13151D] border border-[#EF4444]/20 rounded-[24px] p-6 relative overflow-hidden group">
            <div className="absolute -top-8 -right-8 w-32 h-32 bg-[#EF4444]/10 rounded-full blur-2xl group-hover:bg-[#EF4444]/20 transition-all pointer-events-none"></div>
            <div className="flex items-center gap-2 mb-4">
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20 uppercase tracking-wide">
                ⚠ Warning
              </span>
            </div>
            <p className="text-gray-400 text-xs font-medium uppercase tracking-widest mb-1">Column</p>
            <h4 className="text-xl font-bold text-white mb-4 font-mono">avg_order_value</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Min</span>
                <span className="text-gray-200 font-semibold">$12</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Max</span>
                <span className="text-gray-200 font-semibold">$4,840</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-gray-500">Outliers</span>
                <span className="text-[#EF4444] font-bold">23 detected</span>
              </div>
            </div>
          </div>

          {/* Card 2 - Orange */}
          <div className="bg-[#13151D] border border-[#F59E0B]/20 rounded-[24px] p-6 relative overflow-hidden group">
            <div className="absolute -top-8 -right-8 w-32 h-32 bg-[#F59E0B]/10 rounded-full blur-2xl group-hover:bg-[#F59E0B]/20 transition-all pointer-events-none"></div>
            <div className="flex items-center gap-2 mb-4">
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/20 uppercase tracking-wide">
                ⚠ Warning
              </span>
            </div>
            <p className="text-gray-400 text-xs font-medium uppercase tracking-widest mb-1">Column</p>
            <h4 className="text-xl font-bold text-white mb-4 font-mono">complaint_count</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Min</span>
                <span className="text-gray-200 font-semibold">0</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Max</span>
                <span className="text-gray-200 font-semibold">18</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-gray-500">Outliers</span>
                <span className="text-[#F59E0B] font-bold">11 detected</span>
              </div>
            </div>
          </div>

          {/* Card 3 - Yellow */}
          <div className="bg-[#13151D] border border-[#EAB308]/20 rounded-[24px] p-6 relative overflow-hidden group">
            <div className="absolute -top-8 -right-8 w-32 h-32 bg-[#EAB308]/10 rounded-full blur-2xl group-hover:bg-[#EAB308]/20 transition-all pointer-events-none"></div>
            <div className="flex items-center gap-2 mb-4">
              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-[#EAB308]/10 text-[#EAB308] border border-[#EAB308]/20 uppercase tracking-wide">
                ⚠ Notice
              </span>
            </div>
            <p className="text-gray-400 text-xs font-medium uppercase tracking-widest mb-1">Column</p>
            <h4 className="text-xl font-bold text-white mb-4 font-mono">tenure_months</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Min</span>
                <span className="text-gray-200 font-semibold">1</span>
              </div>
              <div className="flex justify-between items-center py-1.5 border-b border-[#2A2D39]">
                <span className="text-gray-500">Max</span>
                <span className="text-gray-200 font-semibold">84</span>
              </div>
              <div className="flex justify-between items-center py-1.5">
                <span className="text-gray-500">Outliers</span>
                <span className="text-[#EAB308] font-bold">7 detected</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
