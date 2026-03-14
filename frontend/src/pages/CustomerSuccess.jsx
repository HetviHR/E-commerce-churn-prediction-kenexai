import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Users, Star, Filter, ChevronDown, MessageSquare, ArrowUpRight } from 'lucide-react';
import KPICard from '../components/KPICard';

const customerData = [
  { id: 'CUST-8924', city: 'New York', risk: 'High Risk', inactiveDays: 45, complaints: 2, satisfaction: 2.4 },
  { id: 'CUST-7211', city: 'London', risk: 'High Risk', inactiveDays: 32, complaints: 1, satisfaction: 3.1 },
  { id: 'CUST-4490', city: 'San Francisco', risk: 'Medium Risk', inactiveDays: 18, complaints: 0, satisfaction: 3.8 },
  { id: 'CUST-3182', city: 'Berlin', risk: 'Low Risk', inactiveDays: 4, complaints: 0, satisfaction: 4.9 },
  { id: 'CUST-9012', city: 'Toronto', risk: 'Medium Risk', inactiveDays: 21, complaints: 3, satisfaction: 2.8 },
  { id: 'CUST-5543', city: 'Sydney', risk: 'High Risk', inactiveDays: 60, complaints: 4, satisfaction: 1.5 },
];

export default function CustomerSuccess() {
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
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                      row.risk === 'High Risk' ? 'bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/20' : 
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
              <XAxis
                type="number"
                stroke="#6B7280"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="category"
                width={130}
                stroke="#6B7280"
                tick={{ fill: '#E5E7EB', fontSize: 12 }}
                axisLine={false}
                tickLine={false}
              />
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
