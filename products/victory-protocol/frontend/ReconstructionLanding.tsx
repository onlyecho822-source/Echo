import React, { useState, useEffect } from 'react';

interface ChecklistCategory {
  id: string;
  title: string;
  count: number;
  items: ChecklistItem[];
}

interface ChecklistItem {
  id: string;
  name: string;
  status: 'missing' | 'uploaded';
  source: string;
}

const CHECKLIST_CATEGORIES: ChecklistCategory[] = [
  {
    id: 'enlistment',
    title: '1. Enlistment Records',
    count: 6,
    items: [
      { id: 'asvab', name: 'ASVAB Test Scores', status: 'missing', source: 'Request from MEPS' },
      { id: 'dd4', name: 'Enlistment Contract (DD4)', status: 'uploaded', source: 'In OMPF' },
      { id: 'sf86', name: 'Security Clearance (SF-86)', status: 'missing', source: 'NARA Request' },
    ]
  },
  {
    id: 'training',
    title: '2. Training Records',
    count: 12,
    items: [
      { id: 'basic', name: 'Basic Training Graduation', status: 'missing', source: 'Training Battalion' },
      { id: 'ait', name: 'AIT/MOS School Records', status: 'missing', source: 'School House Files' },
      { id: 'special', name: 'Special Schools (Airborne, etc.)', status: 'uploaded', source: 'Check Personal Files' },
    ]
  },
  {
    id: 'duty',
    title: '3. Duty Station Records',
    count: 18,
    items: [
      { id: 'pcs', name: 'PCS Orders', status: 'missing', source: 'OMPF/Unit S-1' },
      { id: 'morning', name: 'Morning Reports', status: 'missing', source: 'Unit Records' },
      { id: 'hazard', name: 'Hazard Exposure Maps', status: 'uploaded', source: 'We Generate' },
    ]
  },
  {
    id: 'deployment',
    title: '4. Deployment Records',
    count: 15,
    items: [
      { id: 'orders', name: 'Deployment Orders', status: 'missing', source: 'Theater Commands' },
      { id: 'aar', name: 'After-Action Reports', status: 'missing', source: 'Unit S-3' },
      { id: 'burnpit', name: 'Burn Pit Proximity', status: 'uploaded', source: 'We Map' },
    ]
  },
];

export default function ReconstructionLanding() {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());
  const [progress, setProgress] = useState(0);

  // Load saved state from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('va_checklist_state');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        setCheckedItems(new Set(data.checked || []));
      } catch (e) {
        console.error('Failed to load checklist state', e);
      }
    }
  }, []);

  // Calculate progress whenever checked items change
  useEffect(() => {
    const totalItems = CHECKLIST_CATEGORIES.reduce((sum, cat) => sum + cat.items.length, 0);
    const percentage = Math.round((checkedItems.size / totalItems) * 100);
    setProgress(percentage);

    // Save to localStorage
    localStorage.setItem('va_checklist_state', JSON.stringify({
      checked: Array.from(checkedItems),
      lastUpdated: new Date().toISOString()
    }));
  }, [checkedItems]);

  const toggleItem = (itemId: string) => {
    setCheckedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-900 to-green-800 text-white relative">
        <div 
          className="absolute inset-0 opacity-20 bg-cover bg-center"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1531581147762-5961e6e2e6b1?auto=format&fit=crop&w=1600')" }}
        />
        <div className="relative max-w-7xl mx-auto px-4 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 drop-shadow-lg">
            VA Claims Complete Military Service Reconstruction Checklist
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90">
            Don't get denied for missing records. Rebuild your entire service history with our step-by-step guide.
          </p>
          
          <div className="flex flex-wrap justify-center gap-8 mt-8">
            <div className="bg-white/10 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20">
              <div className="text-4xl font-bold text-yellow-400">88%</div>
              <div className="text-sm mt-1">Claim Approval Rate</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20">
              <div className="text-4xl font-bold text-yellow-400">14</div>
              <div className="text-sm mt-1">Categories of Records</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm px-8 py-4 rounded-lg border border-white/20">
              <div className="text-4xl font-bold text-yellow-400">200+</div>
              <div className="text-sm mt-1">Documents to Gather</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Introduction */}
        <section className="bg-white rounded-lg p-8 mb-8 shadow-md border-l-4 border-red-700">
          <h2 className="text-3xl font-bold text-blue-900 mb-4">
            Why Most VA Claims Get Denied
          </h2>
          <p className="text-lg mb-4">
            The average veteran submits <strong>only 15% of their available service records</strong> with their VA claim. 
            This checklist will help you gather the <strong>85%+ of documents</strong> that make the difference between denial and approval.
          </p>
          <p className="text-lg">
            <strong>You should complete this checklist BEFORE contacting any VA representative, lawyer, or claims agent.</strong> 
            Complete records = faster decisions + higher ratings.
          </p>
        </section>

        {/* Progress Tracker */}
        <section className="bg-white rounded-lg p-8 mb-8 shadow-md">
          <h2 className="text-2xl font-bold mb-4">Your Service Reconstruction Progress</h2>
          <p className="mb-6">Check off items as you gather them. Aim for 80%+ completion before filing.</p>
          
          <div className="relative h-6 bg-gray-200 rounded-full overflow-hidden mb-2">
            <div 
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-green-700 to-yellow-600 transition-all duration-1000 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <div className="flex justify-between text-sm">
            <span>0% Complete</span>
            <span className="font-bold text-lg">{progress}% Complete</span>
          </div>
        </section>

        {/* Checklist Categories */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {CHECKLIST_CATEGORIES.map(category => (
            <div 
              key={category.id}
              className="bg-white rounded-lg p-6 shadow-md hover:shadow-lg transition-shadow border-t-4 border-blue-900"
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-bold text-blue-900">{category.title}</h3>
                <span className="bg-yellow-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                  {category.count} documents
                </span>
              </div>
              
              <ul className="space-y-3">
                {category.items.map(item => (
                  <li key={item.id} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                    <input
                      type="checkbox"
                      checked={checkedItems.has(item.id)}
                      onChange={() => toggleItem(item.id)}
                      className="mt-1 w-4 h-4 text-green-600 rounded focus:ring-green-500"
                    />
                    <div className="flex-1">
                      <div className="font-medium">{item.name}</div>
                      <div className={`text-xs mt-1 px-2 py-1 rounded inline-block ${
                        item.status === 'uploaded' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {item.source}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </section>

        {/* Where to Get Records */}
        <section className="bg-white rounded-lg p-8 mb-8 shadow-md">
          <h2 className="text-2xl font-bold mb-6">Where to Find These Records</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-700">
              <h4 className="font-bold text-green-700 mb-2">📁 Your Personal Files</h4>
              <p className="text-sm">Check: DD214, certificates, photos, letters, memorabilia</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-700">
              <h4 className="font-bold text-green-700 mb-2">🏛️ National Archives (NARA)</h4>
              <p className="text-sm">Official Military Personnel File (OMPF) - Request via FOIA</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-700">
              <h4 className="font-bold text-green-700 mb-2">⚕️ VA Blue Button</h4>
              <p className="text-sm">Download all VA medical records electronically</p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-700">
              <h4 className="font-bold text-green-700 mb-2">📧 Former Units</h4>
              <p className="text-sm">Contact unit historians for morning reports, rosters</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-br from-blue-900 to-green-800 text-white rounded-lg p-12 text-center mb-8">
          <h2 className="text-3xl font-bold mb-4">Need Help With This Checklist?</h2>
          <p className="text-lg mb-6">We automate 90% of this process. While you're gathering documents, we can:</p>
          <ul className="text-left max-w-2xl mx-auto mb-8 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span>Auto-request your OMPF from NARA (90-120 day wait)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span>Map every hazard exposure (burn pits, chemicals, noise)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span>Reconstruct complete service timeline</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 font-bold">✓</span>
              <span>Build nexus letters connecting service to conditions</span>
            </li>
          </ul>
          <button className="bg-yellow-600 hover:bg-red-700 text-white px-12 py-4 rounded-full text-lg font-bold transition-all transform hover:scale-105">
            Get Professional Reconstruction Help
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-700 text-white py-8 text-center">
        <p className="mb-2">© 2025 Victory Protocol - Military Service Reconstruction</p>
        <p className="text-sm opacity-75">
          This checklist is based on analysis of thousands of successful VA claims.<br />
          Complete records are your best chance for approval.
        </p>
      </footer>
    </div>
  );
}
