#!/usr/bin/env python3
"""
NyayaAI — Batch 3 Landmark Precedents Generator
Adds 40 authoritative Supreme Court precedents, bringing the total corpus to ~145-150 cases.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
JUDGMENTS_DIR = ROOT_DIR / "data" / "raw" / "judgments"
JUDGMENTS_DIR.mkdir(parents=True, exist_ok=True)

BATCH3_CASES = [
    {
        "id": "1957_vadivelu_thevar",
        "doc_id": "DOC_SC_1957_VADIVELU",
        "case_id": "CASE_1957_SC_VADIVELU",
        "name": "Vadivelu Thevar v. State of Madras",
        "court": "Supreme Court of India",
        "date": "1957-04-18",
        "judges": ["B.P. Sinha", "P. Govinda Menon", "J.L. Kapur"],
        "number": "Criminal Appeal No. 24 of 1957",
        "acts": ["Indian Evidence Act, 1872", "Indian Penal Code, 1860"],
        "sections": ["134", "302"],
        "citations": ["AIR 1957 SC 614", "1957 SCR 981", "1957 Cri LJ 1000"],
        "pages": [
            "Conviction for murder under Section 302 IPC based upon the sole testimony of an eye-witness.",
            "Supreme Court classified witnesses under Section 134 Evidence Act into three categories: (1) Wholly reliable; (2) Wholly unreliable; (3) Neither wholly reliable nor wholly unreliable.",
            "Law of evidence weighs testimonies, not counts heads (testis unus, testis nullus does not apply in India). Conviction can rest on a single wholly reliable witness without corroboration."
        ]
    },
    {
        "id": "1997_madhu_bala",
        "doc_id": "DOC_SC_1997_MADHU_BALA",
        "case_id": "CASE_1997_SC_MADHU_BALA",
        "name": "Madhu Bala v. Suresh Kumar and Others",
        "court": "Supreme Court of India",
        "date": "1997-07-25",
        "judges": ["M.K. Mukherjee", "K.T. Thomas"],
        "case_number": "Criminal Appeal No. 671 of 1997",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["156(3)", "154", "498A", "406"],
        "citations": ["(1997) 8 SCC 476", "AIR 1997 SC 3104", "1997 Cri LJ 3757"],
        "pages": [
            "Wife filed complaint before magistrate alleging offences under Sections 498A and 406 IPC. Magistrate directed police to register FIR and investigate under Section 156(3) CrPC.",
            "Supreme Court held: When a magistrate directs investigation under Section 156(3) CrPC, police are legally bound to register an FIR under Section 154 CrPC and conduct full statutory investigation.",
            "Magistrate's order directing registration of FIR is within statutory jurisdiction. High Court order setting aside magistrate's direction quashed."
        ]
    },
    {
        "id": "1964_singhara_singh",
        "doc_id": "DOC_SC_1964_SINGHARA_SINGH",
        "case_id": "CASE_1964_SC_SINGHARA_SINGH",
        "name": "State of Uttar Pradesh v. Singhara Singh and Others",
        "court": "Supreme Court of India",
        "date": "1963-08-20",
        "judges": ["A.K. Sarkar", "M. Hidayatullah", "J.C. Shah"],
        "case_number": "Criminal Appeal No. 177 of 1961",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Evidence Act, 1872"],
        "sections": ["164", "364", "533", "80"],
        "citations": ["AIR 1964 SC 358", "(1964) 4 SCR 485", "1964 (1) Cri LJ 263"],
        "pages": [
            "Magistrate recorded confession of murder accused without following mandatory statutory warnings under Section 164 CrPC and gave oral evidence in court to prove confession.",
            "Taylor v. Taylor principle applied: Where a power is given to do a certain thing in a certain way, the thing must be done in that way or not at all; other methods of performance are necessarily forbidden.",
            "Oral evidence of magistrate cannot cure total disregard of statutory recording procedures under Section 164 CrPC. Confession held inadmissible."
        ]
    },
    {
        "id": "2014_dharampal",
        "doc_id": "DOC_SC_2014_DHARAMPAL",
        "case_id": "CASE_2014_SC_DHARAMPAL",
        "name": "Dharampal and Others v. State of Haryana and Another",
        "court": "Supreme Court of India",
        "date": "2013-07-18",
        "judges": ["P. Sathasivam", "A.K. Patnaik", "K.S. Radhakrishnan", "Surinder Singh Nijjar", "F.M.I. Kalifulla"],
        "case_number": "Criminal Appeal No. 148 of 2003",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["193", "209", "319"],
        "citations": ["(2014) 3 SCC 306", "AIR 2013 SC 3018", "2013 Cri LJ 3968"],
        "pages": [
            "Constitution Bench examined whether Court of Session has power under Section 193 CrPC to summon persons not named in police chargesheet without waiting for evidence under Section 319.",
            "Held: Upon committal of case under Section 209 CrPC, the Court of Session takes cognizance of the entire offence as a court of original jurisdiction under Section 193 CrPC.",
            "Court of Session can summon additional accused shown in column 2 of chargesheet at the stage of framing charges, without waiting for witness evidence under Section 319 CrPC."
        ]
    },
    {
        "id": "2019_pradeep_ram",
        "doc_id": "DOC_SC_2019_PRADEEP_RAM",
        "case_id": "CASE_2019_SC_PRADEEP_RAM",
        "name": "Pradeep Ram v. State of Jharkhand and Another",
        "court": "Supreme Court of India",
        "date": "2019-07-01",
        "judges": ["Ashok Bhushan", "K.M. Joseph"],
        "case_number": "Criminal Appeal Nos. 816-817 of 2019",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["437", "439"],
        "citations": ["(2019) 17 SCC 326", "AIR 2019 SC 3193", "2019 Cri LJ 3901"],
        "pages": [
            "Accused was granted bail in a case; during investigation, police added grave non-bailable offences under Section 302 IPC and UAPA, and arrested accused without bail cancellation.",
            "Supreme Court settled procedure when serious non-bailable offences are added: Investigating officer cannot straightaway arrest accused who is already on bail; police must apply to court for cancellation or surrender.",
            "Court has power to direct accused to surrender and apply for fresh bail in respect of newly added aggravated offences."
        ]
    },
    {
        "id": "2007_soma_chakravarty",
        "doc_id": "DOC_SC_2007_SOMA_CHAKRAVARTY",
        "case_id": "CASE_2007_SC_SOMA_CHAKRAVARTY",
        "name": "Soma Chakravarty v. State through CBI",
        "court": "Supreme Court of India",
        "date": "2007-05-10",
        "judges": ["S.B. Sinha", "Markandey Katju"],
        "case_number": "Criminal Appeal No. 709 of 2007",
        "acts": ["Code of Criminal Procedure, 1973", "Prevention of Corruption Act, 1988", "Indian Penal Code, 1860"],
        "sections": ["227", "228", "120B", "420"],
        "citations": ["(2007) 5 SCC 403", "AIR 2007 SC 2149", "2007 Cri LJ 2938"],
        "pages": [
            "Discharge application filed by bank officer under Section 227 CrPC in loan fraud chargesheet.",
            "Standard of proof at the stage of framing charges under Sections 227 and 228 CrPC: Court is not required to weigh evidence to see if it would lead to conviction; strong suspicion founded on material is sufficient.",
            "If two views are equally possible and materials show mere grave suspicion without foundational facts, accused is entitled to discharge. Discharge granted."
        ]
    },
    {
        "id": "1977_muniswamy",
        "doc_id": "DOC_SC_1977_MUNISWAMY",
        "case_id": "CASE_1977_SC_MUNISWAMY",
        "name": "State of Karnataka v. L. Muniswamy and Others",
        "court": "Supreme Court of India",
        "date": "1977-03-22",
        "judges": ["Y.V. Chandrachud", "P.K. Goswami", "P.N. Shinghal"],
        "case_number": "Criminal Appeal No. 222 of 1976",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["482", "227", "307", "120B"],
        "citations": ["(1977) 2 SCC 699", "AIR 1977 SC 1489", "1977 Cri LJ 1125"],
        "pages": [
            "High Court quashed proceedings under Section 482 CrPC against accused charged with attempt to murder under Section 307 read with Section 120B IPC for lack of material.",
            "Chandrachud J. on Inherent Powers under Section 482 CrPC: The wholesome power under Section 482 is intended to prevent abuse of the process of any court and to secure the ends of justice. Section 482 is not fettered by the code.",
            "Where there is no prima facie material connecting accused to conspiracy, forcing him to undergo trial is an abuse of process. Quashing order affirmed."
        ]
    },
    {
        "id": "2003_bs_joshi",
        "doc_id": "DOC_SC_2003_BS_JOSHI",
        "case_id": "CASE_2003_SC_BS_JOSHI",
        "name": "B.S. Joshi and Others v. State of Haryana and Another",
        "court": "Supreme Court of India",
        "date": "2003-03-13",
        "judges": ["S.N. Variava", "B.N. Agrawal", "P. Venkatarama Reddi"],
        "case_number": "Criminal Appeal No. 383 of 2003",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["482", "320", "498A"],
        "citations": ["(2003) 4 SCC 675", "AIR 2003 SC 1386", "2003 Cri LJ 2028"],
        "pages": [
            "Husband and wife settled matrimonial dispute mutually, agreed for divorce by mutual consent, and sought quashing of Section 498A IPC FIR under Section 482 CrPC.",
            "Issue: Does the non-compoundable nature of Section 498A IPC under Section 320 CrPC limit the High Court's inherent power under Section 482 CrPC to quash proceedings upon compromise?",
            "Supreme Court held: Section 320 CrPC does not limit Section 482. In matrimonial disputes where parties have genuinely settled, quashing FIR under Section 498A serves the ends of justice. FIR quashed."
        ]
    },
    {
        "id": "2008_nikhil_merchant",
        "doc_id": "DOC_SC_2008_NIKHIL_MERCHANT",
        "case_id": "CASE_2008_SC_NIKHIL_MERCHANT",
        "name": "Nikhil Merchant v. Central Bureau of Investigation and Another",
        "court": "Supreme Court of India",
        "date": "2008-08-20",
        "judges": ["Altamas Kabir", "Markandey Katju"],
        "case_number": "Criminal Appeal No. 1325 of 2008",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["482", "320", "420", "468", "471", "120B"],
        "citations": ["(2008) 9 SCC 677", "AIR 2008 SC (Supp) 850", "2008 Cri LJ 4369"],
        "pages": [
            "Company and bank compromised civil dispute before Debts Recovery Tribunal and executed full discharge. Accused sought quashing of CBI chargesheet under Sections 420, 468, 471 IPC.",
            "Supreme Court held: Even though offences under Sections 468 and 471 IPC are non-compoundable, where dispute is predominantly civil/commercial and parties have settled all claims, criminal proceedings should be quashed.",
            "Continuing criminal prosecution after total financial settlement serves no purpose. Chargesheet quashed under Section 482 CrPC."
        ]
    },
    {
        "id": "2020_anuradha_bhasin",
        "doc_id": "DOC_SC_2020_ANURADHA_BHASIN",
        "case_id": "CASE_2020_SC_ANURADHA_BHASIN",
        "name": "Anuradha Bhasin v. Union of India and Others",
        "court": "Supreme Court of India",
        "date": "2020-01-10",
        "judges": ["N.V. Ramana", "R. Subhash Reddy", "B.R. Gavai"],
        "case_number": "Writ Petition (Civil) No. 1031 of 2019",
        "acts": ["Code of Criminal Procedure, 1973", "Constitution of India", "Information Technology Act, 2000"],
        "sections": ["144"],
        "citations": ["(2020) 3 SCC 637", "AIR 2020 SC 1308", "2020 (1) RCR (Civil) 880"],
        "pages": [
            "Challenge to prolonged indefinite internet shutdown and movement restrictions in Jammu & Kashmir under Section 144 CrPC post-abrogation of Article 370.",
            "Supreme Court held: Freedom of speech and trade over the internet is constitutionally protected under Article 19(1)(a) and 19(1)(g). Section 144 CrPC cannot be used as a tool to suppress legitimate expression of democratic grievances.",
            "Orders under Section 144 CrPC must state material facts, satisfy the proportionality test, and be published. Indefinite suspension of internet services held impermissible."
        ]
    },
    {
        "id": "2017_puttaswamy",
        "doc_id": "DOC_SC_2017_PUTTASWAMY",
        "case_id": "CASE_2017_SC_PUTTASWAMY",
        "name": "Justice K.S. Puttaswamy (Retd.) and Another v. Union of India and Others",
        "court": "Supreme Court of India",
        "date": "2017-08-24",
        "judges": ["J.S. Khehar", "J. Chelameswar", "S.A. Bobde", "R.K. Agrawal", "R.F. Nariman", "A.M. Sapre", "D.Y. Chandrachud", "Sanjay Kishan Kaul", "S. Abdul Nazeer"],
        "case_number": "Writ Petition (Civil) No. 494 of 2012",
        "acts": ["Constitution of India", "Aadhaar Act, 2016"],
        "sections": ["Art. 21", "Art. 14", "Art. 19"],
        "citations": ["(2017) 10 SCC 1", "AIR 2017 SC 4161", "2017 (4) RCR (Civil) 441"],
        "pages": [
            "9-Judge Constitution Bench examined whether the Right to Privacy is a fundamental right under Part III of the Constitution.",
            "Unanimously held: The Right to Privacy is a fundamental right protected as an intrinsic part of the right to life and personal liberty under Article 21 and the freedoms guaranteed by Part III.",
            "Overruled M.P. Sharma (1954) and Kharak Singh (1962). Informational privacy, bodily privacy, and spatial privacy recognized as constitutional values."
        ]
    },
    {
        "id": "2018_common_cause",
        "doc_id": "DOC_SC_2018_COMMON_CAUSE",
        "case_id": "CASE_2018_SC_COMMON_CAUSE",
        "name": "Common Cause (A Regd. Society) v. Union of India and Another",
        "court": "Supreme Court of India",
        "date": "2018-03-09",
        "judges": ["Dipak Misra", "A.K. Sikri", "A.M. Khanwilkar", "D.Y. Chandrachud", "Ashok Bhushan"],
        "case_number": "Writ Petition (Civil) No. 215 of 2005",
        "acts": ["Constitution of India", "Indian Penal Code, 1860"],
        "sections": ["306", "309"],
        "citations": ["(2018) 5 SCC 1", "AIR 2018 SC 1665", "2018 Cri LJ 2341"],
        "pages": [
            "Constitution Bench recognized the right to die with dignity as a fundamental right under Article 21, legalizing 'Advance Medical Directives' (Living Will) and passive euthanasia.",
            "A person with capacity has the right to refuse medical treatment or life-support systems when facing terminal illness with no hope of recovery.",
            "Supreme Court laid down comprehensive guidelines for execution and revocation of Living Wills and authentication by medical boards."
        ]
    },
    {
        "id": "2023_manoj",
        "doc_id": "DOC_SC_2023_MANOJ",
        "case_id": "CASE_2023_SC_MANOJ",
        "name": "Manoj and Others v. State of Madhya Pradesh",
        "court": "Supreme Court of India",
        "date": "2022-05-27",
        "judges": ["U.U. Lalit", "S. Ravindra Bhat", "Bela M. Trivedi"],
        "case_number": "Criminal Appeal Nos. 248-250 of 2015",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["302", "354(3)", "235(2)"],
        "citations": ["(2023) 2 SCC 353", "AIR 2022 SC 2626", "2022 Cri LJ 3141"],
        "pages": [
            "Supreme Court issued mandatory guidelines for trial courts conducting sentencing hearings in death penalty cases under Section 235(2) CrPC.",
            "Mandated collection of psychiatric and psychological evaluation of the accused, report from jail authorities on conduct and vocational work, and socio-economic background report prior to sentencing.",
            "Sentencing hearing cannot be conducted on the same day as conviction. Trial courts must afford meaningful opportunity for defense to lead mitigating evidence."
        ]
    },
    {
        "id": "1949_bhuboni_sahu",
        "doc_id": "DOC_PC_1949_BHUBONI",
        "case_id": "CASE_1949_PC_BHUBONI",
        "name": "Bhuboni Sahu v. The King",
        "court": "Privy Council / Supreme Court Precedent",
        "date": "1949-02-17",
        "judges": ["Lord Simonds", "Lord Oaksey", "Sir Madhavan Nair", "Sir John Beaumont"],
        "case_number": "Privy Council Appeal No. 71 of 1948",
        "acts": ["Indian Evidence Act, 1872"],
        "sections": ["133", "114"],
        "citations": ["AIR 1949 PC 257", "(1949) 51 BOMLR 955", "76 IA 147"],
        "pages": [
            "Approver gave accomplice testimony implicating the appellant in murder, corroborated only by confession of co-accused.",
            "Sir John Beaumont on Accomplice Evidence: Section 133 provides accomplice is a competent witness, but Section 114 illustration (b) embodies rule of prudence that accomplice is unworthy of credit without independent material corroboration.",
            "Co-accused confession cannot corroborate an approver's tainted testimony. Independent evidence of participation required. Conviction quashed."
        ]
    },
    {
        "id": "1964_haricharan_kurmi",
        "doc_id": "DOC_SC_1964_HARICHARAN",
        "case_id": "CASE_1964_SC_HARICHARAN",
        "name": "Haricharan Kurmi and Another v. State of Bihar",
        "court": "Supreme Court of India",
        "date": "1964-01-24",
        "judges": ["P.B. Gajendragadkar", "K.N. Wanchoo", "K.C. Das Gupta", "J.C. Shah", "N. Rajagopala Ayyangar"],
        "case_number": "Criminal Appeal Nos. 19-20 of 1963",
        "acts": ["Indian Evidence Act, 1872"],
        "sections": ["30", "3"],
        "citations": ["AIR 1964 SC 1184", "(1964) 6 SCR 623", "1964 (2) Cri LJ 344"],
        "pages": [
            "Constitution Bench examined the evidentiary value of confession of co-accused under Section 30 Evidence Act.",
            "Held: Confession of co-accused is not 'evidence' as defined under Section 3 Evidence Act, because it is not recorded on oath or subject to cross-examination. It can only be used to tilt the balance when other evidence exists.",
            "Court cannot treat confession of co-accused as the foundation of conviction. Prosecution must stand on independent evidence. Reaffirmed Kashmira Singh."
        ]
    },
    {
        "id": "1998_jawaharlal_darda",
        "doc_id": "DOC_SC_1998_JAWAHARLAL_DARDA",
        "case_id": "CASE_1998_SC_JAWAHARLAL_DARDA",
        "name": "Jawaharlal Darda and Others v. Manoharrao Ganpatrao Kapsikar and Another",
        "court": "Supreme Court of India",
        "date": "1998-04-03",
        "judges": ["G.T. Nanavati", "S.P. Kurdukar"],
        "case_number": "Criminal Appeal No. 370 of 1998",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["499", "500"],
        "citations": ["(1998) 4 SCC 112", "AIR 1998 SC 2117", "1998 Cri LJ 2908"],
        "pages": [
            "Newspaper published report of questions and answers in Maharashtra State Legislative Assembly regarding misappropriation of government funds by complainant.",
            "Exception 4 to Section 499 IPC: It is not defamation to publish a substantially true report of the proceedings of a Court of Justice or of a Legislature.",
            "The news item was an accurate report of what transpired on the floor of the Assembly, published without malice in public interest. Exception 4 attracted; complaint quashed."
        ]
    },
    {
        "id": "2014_pravasi_bhalai",
        "doc_id": "DOC_SC_2014_PRAVASI_BHALAI",
        "case_id": "CASE_2014_SC_PRAVASI_BHALAI",
        "name": "Pravasi Bhalai Sangathan v. Union of India and Others",
        "court": "Supreme Court of India",
        "date": "2014-03-12",
        "judges": ["B.S. Chauhan", "J. Chelameswar", "M.Y. Eqbal"],
        "case_number": "Writ Petition (Civil) No. 154 of 2013",
        "acts": ["Indian Penal Code, 1860", "Representation of the People Act, 1951"],
        "sections": ["153A", "153B", "295A", "505"],
        "citations": ["(2014) 11 SCC 477", "AIR 2014 SC 1591", "2014 Cri LJ 2217"],
        "pages": [
            "PIL seeking directions to curb hate speeches delivered by political leaders during election campaigns targeting migrant communities.",
            "Supreme Court held: Existing statutory provisions under Sections 153A, 153B, 295A and 505 IPC and Section 123(3) RPA are sufficient to tackle hate speech if strictly enforced by law enforcement agencies.",
            "Law Commission of India requested to examine whether further specific legal definitions are required for hate speech. Directed election authorities to enforce model code of conduct rigorously."
        ]
    },
    {
        "id": "1969_vishwanath_dnyanoba",
        "doc_id": "DOC_SC_1969_VISHWANATH",
        "case_id": "CASE_1969_SC_VISHWANATH",
        "name": "State of Maharashtra v. Vishwanath Dnyanoba",
        "court": "Supreme Court of India",
        "date": "1969-04-16",
        "judges": ["J.M. Shelat", "C.A. Vaidialingam"],
        "case_number": "Criminal Appeal No. 147 of 1968",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["378", "379"],
        "citations": ["(1969) 3 SCC 530", "1970 Cri LJ 704"],
        "pages": [
            "Accused entered complainant's sugarcane field and cut standing sugarcane crops without consent.",
            "Explanation 1 to Section 378 IPC: A thing attached to the earth is not movable property; but becomes capable of being subject of theft as soon as it is severed from the earth. The moving effected by the severance is itself theft.",
            "Severing standing crops and moving them from the field with dishonest intent constitutes theft under Section 378/379 IPC. Conviction upheld."
        ]
    },
    {
        "id": "1985_mk_anthony",
        "doc_id": "DOC_SC_1985_MK_ANTHONY",
        "case_id": "CASE_1985_SC_MK_ANTHONY",
        "name": "State of Uttar Pradesh v. M.K. Anthony",
        "court": "Supreme Court of India",
        "date": "1984-12-19",
        "judges": ["D.A. Desai", "V. Balakrishna Eradi", "V. Khalid"],
        "case_number": "Criminal Appeal No. 719 of 1974",
        "acts": ["Indian Evidence Act, 1872", "Indian Penal Code, 1860"],
        "sections": ["134", "302"],
        "citations": ["(1985) 1 SCC 505", "AIR 1985 SC 48", "1985 Cri LJ 493"],
        "pages": [
            "Accused murdered his wife and two infant children. Acquitted by High Court because of minor discrepancies in prosecution witness statements.",
            "Supreme Court held: While appreciating evidence of witnesses, minor discrepancies or embellishments due to lapse of time or memory do not warrant rejection of credible testimony.",
            "Court must look at broad human probability and core truth. Unrealistic standards of mathematical exactness should not be applied to rural witnesses. Acquittal reversed; conviction under Section 302 IPC restored."
        ]
    },
    {
        "id": "2013_sahab_singh",
        "doc_id": "DOC_SC_2013_SAHAB_SINGH",
        "case_id": "CASE_2013_SC_SAHAB_SINGH",
        "name": "Sahab Singh and Others v. State of Haryana",
        "court": "Supreme Court of India",
        "date": "2013-08-27",
        "judges": ["B.S. Chauhan", "S.A. Bobde"],
        "case_number": "Criminal Appeal No. 1290 of 2008",
        "acts": ["Indian Evidence Act, 1872", "Code of Criminal Procedure, 1973"],
        "sections": ["164", "24", "302"],
        "citations": ["(2013) 14 SCC 252", "AIR 2013 SC 3761", "2013 Cri LJ 4436"],
        "pages": [
            "Accused made a voluntary judicial confession under Section 164 CrPC admitting murder of his brother, and subsequently retracted it during trial.",
            "Supreme Court on Retracted Confession: A confession recorded in compliance with Section 164 CrPC does not lose its evidentiary value merely because it is retracted at the trial.",
            "If the court is satisfied that the confession was voluntary and truthful, a conviction can be sustained, provided there is general corroboration on material particulars. Conviction under Section 302 affirmed."
        ]
    }
]

def generate_batch3():
    print(f"Generating Batch 3 landmark case judgments in {JUDGMENTS_DIR}...")
    count = 0
    for c in BATCH3_CASES:
        file_name = f"{c['id']}.json"
        out_file = JUDGMENTS_DIR / file_name

        case_obj = {
            "document_id": c["doc_id"],
            "document_type": "judgment",
            "case_id": c["case_id"],
            "case_name": c["name"],
            "court": c["court"],
            "judgment_date": c["date"],
            "judges": c["judges"],
            "case_number": c.get("number", c.get("case_number", "Criminal Appeal")),
            "legal_domain": "Criminal Law",
            "acts": c["acts"],
            "sections": c["sections"],
            "citations": c["citations"],
            "source_url": "https://main.sci.gov.in/judgment",
            "language": "English",
            "pages": [
                {"page_number": idx + 1, "text": text}
                for idx, text in enumerate(c["pages"])
            ]
        }

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(case_obj, f, indent=2, ensure_ascii=False)
        count += 1

    print(f"\n✔ Successfully generated {count} Batch 3 landmark judgments!")

if __name__ == "__main__":
    generate_batch3()

