import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, ArrowRightLeft, Search, Sparkles, Scale, BookOpen } from 'lucide-react';

export default function ActsPage() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('all');
  const [search, setSearch] = useState('');

  // Comprehensive Statutory Concordance Database
  const statutoryProvisions = [
    // IPC to BNS (Property & Financial Offences)
    {
      category: 'penal_code',
      topic: 'Theft (Substantive Definition)',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 378',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 303(1)',
      key_changes: 'Retains five classic elements (dishonest intention, movable property, possession, without consent, moving).',
    },
    {
      category: 'penal_code',
      topic: 'Punishment for Theft',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 379',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 303(2)',
      key_changes: 'Imprisonment up to 3 years or fine; community service introduced for petty first-time theft (< ₹5,000).',
    },
    {
      category: 'penal_code',
      topic: 'Criminal Breach of Trust (Definition & Punishment)',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 405 & 406',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 316',
      key_changes: 'Consolidated definition and graded punishments up to 5 years for entrustment violations.',
    },
    {
      category: 'penal_code',
      topic: 'Cheating and Dishonestly Inducing Delivery of Property',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 415 & 420',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 318(1) & 318(4)',
      key_changes: 'Requires fraudulent or dishonest intention at inception; imprisonment up to 7 years.',
    },
    {
      category: 'penal_code',
      topic: 'Dowry Death & Statutory Presumption',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 304B',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 80',
      key_changes: 'Preserves 7-year death window and cruelty requirement immediately preceding death.',
    },
    {
      category: 'penal_code',
      topic: 'Cruelty by Husband or Relatives of Husband',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 498A',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 85 & 86',
      key_changes: 'Separates cruelty definition from penalty; applies Arnesh Kumar notice protections.',
    },
    {
      category: 'penal_code',
      topic: 'Murder (Definition & Punishment)',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 300 & 302',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 101 & 103(1)',
      key_changes: 'Death or life imprisonment; introduces Section 103(2) for mob lynching / hate crimes.',
    },
    {
      category: 'penal_code',
      topic: 'Culpable Homicide Not Amounting to Murder',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 299 & 304',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 100 & 105',
      key_changes: 'Distinguishes Part I (intention) and Part II (knowledge) liability.',
    },
    {
      category: 'penal_code',
      topic: 'Criminal Conspiracy',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 120A & 120B',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 61',
      key_changes: 'Agreement to commit illegal act; restructured under Chapter IV of BNS.',
    },
    {
      category: 'penal_code',
      topic: 'Forgery & Using Forged Document as Genuine',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 463, 465, 471',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 336, 338, 340',
      key_changes: 'Covers electronic and digital records explicitly.',
    },
    {
      category: 'penal_code',
      topic: 'Defamation (Definition & Exception)',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 499 & 500',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 356',
      key_changes: 'Simple imprisonment up to 2 years, fine, or community service.',
    },
    {
      category: 'penal_code',
      topic: 'Criminal Intimidation',
      old_act: 'Indian Penal Code, 1860 (IPC)',
      old_section: 'Section 503 & 506',
      new_act: 'Bharatiya Nyaya Sanhita, 2023 (BNS)',
      new_section: 'Section 351',
      key_changes: 'Threat of injury to person, reputation, or property.',
    },

    // CrPC to BNSS (Procedural & Bail Law)
    {
      category: 'criminal_procedure',
      topic: 'Anticipatory Bail (Direction for grant of bail to person apprehending arrest)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 438',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 482',
      key_changes: 'Retains landmark principles from Gurbaksh Sibbia and Sushila Aggarwal; high court and sessions court concurrent jurisdiction.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Special Powers of High Court / Sessions Court Regarding Regular Bail',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 439',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 483',
      key_changes: 'Jurisprudence of Satender Kumar Antil preserved; broad discretion on reasonable conditions.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Notice of Appearance before Police Officer / Safeguards against arbitrary arrest',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 41A',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 35',
      key_changes: 'Requires prior permission of Deputy SP for arresting elderly/infirm in offences punishable under 3 years; codifies Arnesh Kumar.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Inherent Powers of High Court to Quash FIR & Prevent Abuse of Process',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 482',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 528',
      key_changes: 'Preserves the entire jurisprudence laid down in State of Haryana v. Bhajan Lal.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Bail in Bailable Offences (Mandatory Right to Bail)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 436',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 478',
      key_changes: 'Mandatory release on bond for indigent undertrials unable to furnish surety.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Maximum Period for Undertrial Detention (Default release)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 436A',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 479',
      key_changes: 'First-time offenders eligible for bail after serving one-third of maximum sentence instead of one-half.',
    },
    {
      category: 'criminal_procedure',
      topic: 'Information in Cognizable Cases (Mandatory FIR Registration)',
      old_act: 'Code of Criminal Procedure, 1973 (CrPC)',
      old_section: 'Section 154',
      new_act: 'Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)',
      new_section: 'Section 173',
      key_changes: 'Expressly provides for e-FIR / Zero FIR registration nationwide within 3 days.',
    },

    // IT Act Cyber Offences
    {
      category: 'it_act',
      topic: 'Punishment for sending offensive messages through communication services (Struck Down)',
      old_act: 'Information Technology Act, 2000',
      old_section: 'Section 66A',
      new_act: 'UNCONSTITUTIONAL (Shreya Singhal v. Union of India, 2015)',
      new_section: 'Struck Down under Article 19(1)(a)',
      key_changes: 'Violated Fundamental Right to Free Speech. Police prohibited from registering FIRs.',
    },
    {
      category: 'it_act',
      topic: 'Identity Theft / Fraudulent use of Electronic Signature or Password',
      old_act: 'Information Technology Act, 2000',
      old_section: 'Section 66C',
      new_act: 'Active IT Act Cyber Law',
      new_section: 'Section 66C',
      key_changes: 'Imprisonment up to 3 years and fine up to ₹1,00,000.',
    },
    {
      category: 'it_act',
      topic: 'Cheating by Personation by using computer resource',
      old_act: 'Information Technology Act, 2000',
      old_section: 'Section 66D',
      new_act: 'Active IT Act Cyber Law',
      new_section: 'Section 66D',
      key_changes: 'Imprisonment up to 3 years and fine up to ₹1,00,000.',
    },
  ];

  const filteredProvisions = statutoryProvisions.filter((item) => {
    const matchesCategory = activeTab === 'all' || item.category === activeTab;
    const q = search.trim().toLowerCase();
    if (!q) return matchesCategory;

    const matchesSearch =
      item.topic.toLowerCase().includes(q) ||
      item.old_section.toLowerCase().includes(q) ||
      item.new_section.toLowerCase().includes(q) ||
      item.old_act.toLowerCase().includes(q) ||
      item.new_act.toLowerCase().includes(q) ||
      item.key_changes.toLowerCase().includes(q);

    return matchesCategory && matchesSearch;
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6 pb-6 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <FileText className="w-6 h-6 text-emerald-400" />
              Indian Statutory Bare Acts & Section Search
            </h1>
            <p className="text-xs text-slate-400 mt-1">
              Search and compare statutory provisions across Indian Penal Code (IPC 1860) ⇄ Bharatiya Nyaya Sanhita (BNS 2023) and CrPC ⇄ BNSS
            </p>
          </div>

          <div className="text-xs font-semibold px-3.5 py-1.5 rounded-xl bg-emerald-950/60 border border-emerald-800/40 text-emerald-300">
            {filteredProvisions.length} Statutory Provisions Found
          </div>
        </div>

        {/* Search Bar */}
        <div className="relative mb-6">
          <Search className="w-5 h-5 text-slate-400 absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by section number or offence (e.g. 378, 420, 438, 303, 318, 482, theft, bail, cheating)..."
            className="w-full pl-12 pr-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-emerald-500 shadow-md"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
            >
              Clear
            </button>
          )}
        </div>

        {/* Tab Selection */}
        <div className="flex flex-wrap items-center gap-2 mb-6 border-b border-slate-800 pb-3">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'all'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-900'
            }`}
          >
            All Acts & Codes ({statutoryProvisions.length})
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

        {/* Results Grid */}
        {filteredProvisions.length === 0 ? (
          <div className="py-16 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
            <Search className="w-8 h-8 text-slate-500 mx-auto mb-2" />
            <div className="text-sm font-semibold">No statutory provisions matching "{search}"</div>
            <div className="text-xs text-slate-500 mt-1">Try searching for Section 378, 420, 438, theft, or bail.</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredProvisions.map((item, idx) => (
              <div
                key={idx}
                className="bg-slate-900 p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/40 transition-all shadow-lg"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 mb-3">
                  <div>
                    <h3 className="text-sm sm:text-base font-bold text-white">{item.topic}</h3>
                    <div className="text-[11px] text-slate-400 mt-0.5">
                      {item.category === 'penal_code' ? 'Substantive Criminal Law' : item.category === 'criminal_procedure' ? 'Procedural Criminal Law' : 'Cyber & Special Law'}
                    </div>
                  </div>

                  <button
                    onClick={() =>
                      navigate(`/?q=${encodeURIComponent(item.topic + ' ' + item.old_section + ' ' + item.new_section)}`)
                    }
                    className="px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 text-xs font-semibold flex items-center gap-1.5 transition-colors self-start"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                    Analyze in AI
                  </button>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-blue-400 font-bold uppercase block">
                      Historical Provision (Pre-July 2024)
                    </span>
                    <div className="text-sm font-extrabold text-white mt-1">
                      {item.old_section}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">{item.old_act}</div>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-emerald-400 font-bold uppercase block">
                      In-Force Provision (Effective 1 July 2024)
                    </span>
                    <div className="text-sm font-extrabold text-white mt-1">
                      {item.new_section}
                    </div>
                    <div className="text-xs text-slate-400 mt-0.5">{item.new_act}</div>
                  </div>
                </div>

                <div className="text-xs text-slate-300 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                  <span className="font-semibold text-slate-400">Legislative & Judicial Impact: </span>
                  {item.key_changes}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
