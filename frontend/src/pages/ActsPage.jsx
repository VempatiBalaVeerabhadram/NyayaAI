import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, ArrowRightLeft, Search, Sparkles, BookOpen, ChevronRight, Scale } from 'lucide-react';

export default function ActsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('criminal_procedure');
  const [search, setSearch] = useState('');

  // Indian Statutory Comparative Mapping
  const crpcToBnss = [
    {
      topic: 'Anticipatory Bail (Direction for grant of bail to person apprehending arrest)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 438',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 482',
      key_changes: 'Retains landmark principles from Gurbaksh Sibbia and Sushila Aggarwal; high court and sessions court concurrent jurisdiction.',
    },
    {
      topic: 'Notice of Appearance before Police Officer / Safeguards against arbitrary arrest',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 41A',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 35',
      key_changes: 'Requires prior permission of Deputy SP for arresting elderly/infirm in offences punishable under 3 years; codifies Arnesh Kumar.',
    },
    {
      topic: 'Bail in Bailable Offences (Right to bail)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 436',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 478',
      key_changes: 'Mandatory release on bond for indigent undertrials.',
    },
    {
      topic: 'Maximum Period for Undertrial Detention (Default release)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 436A',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 479',
      key_changes: 'First-time offenders eligible for bail after serving one-third of maximum sentence instead of one-half.',
    },
    {
      topic: 'Inherent Powers of High Court to Quash FIR & Prevent Abuse of Process',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 482',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 528',
      key_changes: 'Preserves the entire jurisprudence laid down in Bhajan Lal and Gian Singh.',
    },
    {
      topic: 'Information in Cognizable Cases (Mandatory FIR Registration)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 154',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 173',
      key_changes: 'Expressly provides for e-FIR / Zero FIR registration nationwide within 3 days.',
    },
  ];

  const ipcToBns = [
    {
      topic: 'Cheating and Dishonestly Inducing Delivery of Property',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 420',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 318(4)',
      key_changes: 'Consolidates cheating definitions with imprisonment up to 7 years and fine.',
    },
    {
      topic: 'Criminal Breach of Trust (Definition & Punishment)',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 405 & 406',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 316',
      key_changes: 'Combined definition and graded punishments for entrustment violations.',
    },
    {
      topic: 'Acts Done in Furtherance of Common Intention',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 34',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 3(5)',
      key_changes: 'Harmonized general explanation for joint criminal liability.',
    },
    {
      topic: 'Criminal Conspiracy',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 120B',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 61(2)',
      key_changes: 'Restructured under Chapter IV of BNS.',
    },
  ];

  const itActProvisions = [
    {
      topic: 'Punishment for sending offensive messages through communication services (Struck Down)',
      act: 'Information Technology Act, 2000',
      section: 'Section 66A',
      status: 'UNCONSTITUTIONAL (Shreya Singhal v. Union of India, 2015)',
      holding: 'Violated Fundamental Right to Free Speech under Article 19(1)(a). Overbroad and vague.',
    },
    {
      topic: 'Identity Theft / Fraudulent use of Electronic Signature or Password',
      act: 'Information Technology Act, 2000',
      section: 'Section 66C',
      status: 'Active Law',
      holding: 'Imprisonment up to 3 years and fine up to 1 lakh rupees.',
    },
    {
      topic: 'Cheating by Personation by using computer resource',
      act: 'Information Technology Act, 2000',
      section: 'Section 66D',
      status: 'Active Law',
      holding: 'Imprisonment up to 3 years and fine up to 1 lakh rupees.',
    },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 pb-6 border-b border-slate-800">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-emerald-400" />
            Indian Statutory Bare Acts & Comparative Concordance
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Compare Old Criminal Codes (CrPC 1973, IPC 1860) with New Sanhitas (BNSS 2023, BNS 2023) and IT Act 2000 provisions
          </p>
        </div>

        {/* Tab Selection */}
        <div className="flex items-center gap-2 mb-6 border-b border-slate-800 pb-3">
          <button
            onClick={() => setActiveTab('criminal_procedure')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'criminal_procedure'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            CrPC (1973) ⇄ BNSS (2023)
          </button>

          <button
            onClick={() => setActiveTab('penal_code')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'penal_code'
                ? 'bg-amber-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            IPC (1860) ⇄ BNS (2023)
          </button>

          <button
            onClick={() => setActiveTab('it_act')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'it_act'
                ? 'bg-purple-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            IT Act (2000) Cyber Offences
          </button>
        </div>

        {/* Content Tabs */}
        {activeTab === 'criminal_procedure' && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-800/40 text-xs text-blue-200 mb-4">
              <strong>Procedural Law Transition:</strong> CrPC 1973 bail, arrest, and quashing provisions correspond directly to Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 sections.
            </div>

            <div className="grid grid-cols-1 gap-4">
              {crpcToBnss.map((item, idx) => (
                <div
                  key={idx}
                  className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-blue-500/40 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h3 className="text-sm font-bold text-white">{item.topic}</h3>
                    <button
                      onClick={() =>
                        navigate(`/search?q=${encodeURIComponent(item.topic + ' ' + item.old_section + ' ' + item.new_section)}`)
                      }
                      className="px-3 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 text-xs font-semibold flex items-center gap-1 transition-colors flex-shrink-0"
                    >
                      <Sparkles className="w-3 h-3 text-amber-300" />
                      Search AI
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-700/60">
                      <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                        Old Act (CrPC 1973)
                      </span>
                      <span className="text-sm font-bold text-amber-400 block mt-0.5">
                        {item.old_section}
                      </span>
                      <span className="text-[11px] text-slate-400 block">{item.old_act}</span>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-700/60">
                      <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                        New Sanhita (BNSS 2023)
                      </span>
                      <span className="text-sm font-bold text-emerald-400 block mt-0.5">
                        {item.new_section}
                      </span>
                      <span className="text-[11px] text-slate-400 block">{item.new_act}</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <strong className="text-slate-200">Legal Nuance & Evolution:</strong>{' '}
                    {item.key_changes}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'penal_code' && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-800/40 text-xs text-amber-200 mb-4">
              <strong>Substantive Criminal Law Concordance:</strong> Indian Penal Code (IPC 1860) offences mapped to Bharatiya Nyaya Sanhita (BNS 2023).
            </div>

            <div className="grid grid-cols-1 gap-4">
              {ipcToBns.map((item, idx) => (
                <div
                  key={idx}
                  className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-amber-500/40 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <h3 className="text-sm font-bold text-white">{item.topic}</h3>
                    <button
                      onClick={() =>
                        navigate(`/search?q=${encodeURIComponent(item.topic + ' ' + item.old_section + ' ' + item.new_section)}`)
                      }
                      className="px-3 py-1 rounded-lg bg-amber-600/20 hover:bg-amber-600/40 text-amber-300 text-xs font-semibold flex items-center gap-1 transition-colors flex-shrink-0"
                    >
                      <Sparkles className="w-3 h-3 text-amber-300" />
                      Search AI
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-700/60">
                      <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                        Old Act (IPC 1860)
                      </span>
                      <span className="text-sm font-bold text-amber-400 block mt-0.5">
                        {item.old_section}
                      </span>
                      <span className="text-[11px] text-slate-400 block">{item.old_act}</span>
                    </div>

                    <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-700/60">
                      <span className="text-[10px] text-slate-400 font-semibold uppercase block">
                        New Sanhita (BNS 2023)
                      </span>
                      <span className="text-sm font-bold text-emerald-400 block mt-0.5">
                        {item.new_section}
                      </span>
                      <span className="text-[11px] text-slate-400 block">{item.new_act}</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <strong className="text-slate-200">Statutory Restructuring:</strong>{' '}
                    {item.key_changes}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'it_act' && (
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-purple-950/40 border border-purple-800/40 text-xs text-purple-200 mb-4">
              <strong>Cyber Law Jurisprudence:</strong> Information Technology Act, 2000 provisions including Constitutional invalidation of Section 66A.
            </div>

            <div className="grid grid-cols-1 gap-4">
              {itActProvisions.map((item, idx) => (
                <div
                  key={idx}
                  className="glass-card p-5 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <h3 className="text-sm font-bold text-white">{item.topic}</h3>
                      <span className="text-xs font-mono text-purple-400 mt-0.5 block">
                        {item.act} — {item.section}
                      </span>
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                        item.status.includes('UNCONSTITUTIONAL')
                          ? 'bg-red-950 text-red-300 border border-red-800'
                          : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                      }`}
                    >
                      {item.status}
                    </span>
                  </div>

                  <p className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                    <strong className="text-slate-200">Legal Holding / Penalty:</strong>{' '}
                    {item.holding}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
