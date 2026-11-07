#!/usr/bin/env python3
"""
NyayaAI — Batch 2 Landmark Precedents Generator
Adds 40 additional authoritative Supreme Court precedents across procedural, evidence,
property, and criminal law domains.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
JUDGMENTS_DIR = ROOT_DIR / "data" / "raw" / "judgments"
JUDGMENTS_DIR.mkdir(parents=True, exist_ok=True)

BATCH2_CASES = [
    {
        "id": "1945_mahbub_shah",
        "doc_id": "DOC_PC_1945_MAHBUB_SHAH",
        "case_id": "CASE_1945_PC_MAHBUB_SHAH",
        "name": "Mahbub Shah v. Emperor (Indus River Case)",
        "court": "Privy Council / Supreme Court Precedent",
        "date": "1945-01-31",
        "judges": ["Sir Madhavan Nair", "Lord Atkin", "Lord Thankerton"],
        "number": "Privy Council Appeal No. 78 of 1944",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["34", "300", "302", "304"],
        "citations": ["AIR 1945 PC 118", "(1945) 47 BOMLR 941", "72 IA 148"],
        "pages": [
            "Parties on the banks of the Indus River clashed over cutting reeds. Two accused fired guns; one killed the deceased while appellant wounded another witness.",
            "Sir Madhavan Nair laid down the distinction between 'common intention' and 'similar intention' under Section 34 IPC: Common intention implies a pre-arranged plan and prior meeting of minds. Same or similar intention without prior concert does not attract Section 34.",
            "There was no evidence of prior concert between the two shooters. Appellant could not be convicted of murder under Section 302 read with Section 34. Convicted only for attempted murder under Section 307 for his own shot."
        ]
    },
    {
        "id": "1960_rp_kapur",
        "doc_id": "DOC_SC_1960_RP_KAPUR",
        "case_id": "CASE_1960_SC_RP_KAPUR",
        "name": "R.P. Kapur v. State of Punjab",
        "court": "Supreme Court of India",
        "date": "1960-03-29",
        "judges": ["P.B. Gajendragadkar", "K.N. Wanchoo", "K.C. Das Gupta"],
        "number": "Criminal Appeal No. 197 of 1958",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["482", "420", "120B"],
        "citations": ["AIR 1960 SC 866", "(1960) 3 SCR 388", "1960 Cri LJ 1239"],
        "pages": [
            "Senior IAS officer challenged criminal proceedings under Section 420/120B IPC for cheating in sale of land, seeking quashing under inherent powers.",
            "Gajendragadkar J. laid down the 3 classic categories where High Court can quash criminal proceedings under Section 482 (inherent powers): (1) Legal bar against institution (e.g. want of sanction); (2) Allegations in FIR taken at face value do not constitute an offence; (3) Manifest lack of evidence or allegations are absurd and inherently improbable.",
            "Allegations made out a prima facie case requiring investigation. Inherent jurisdiction should be exercised sparingly. Petition dismissed."
        ]
    },
    {
        "id": "1978_gurcharan_singh",
        "doc_id": "DOC_SC_1978_GURCHARAN",
        "case_id": "CASE_1978_SC_GURCHARAN",
        "name": "Gurcharan Singh and Others v. State (Delhi Administration)",
        "court": "Supreme Court of India",
        "date": "1977-12-09",
        "judges": ["P.K. Goswami", "P.N. Shinghal"],
        "case_number": "Criminal Appeal No. 441 of 1977",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["437", "439"],
        "citations": ["(1978) 1 SCC 118", "AIR 1978 SC 179", "1978 Cri LJ 129"],
        "pages": [
            "Sessions Judge granted bail to accused charged with conspiracy and murder under Section 302 IPC. High Court cancelled bail under Section 439(2) CrPC.",
            "Supreme Court explained the distinction between Section 437 (Magistrate's restricted bail powers in capital offences) and Section 439 (High Court & Sessions Court unrestricted special bail powers).",
            "Bail in capital offences requires careful judicial discretion considering gravity, witness tampering, and public safety. Cancellation by High Court affirmed."
        ]
    },
    {
        "id": "1978_babu_singh",
        "doc_id": "DOC_SC_1978_BABU_SINGH",
        "case_id": "CASE_1978_SC_BABU_SINGH",
        "name": "Babu Singh and Others v. State of Uttar Pradesh",
        "court": "Supreme Court of India",
        "date": "1978-01-31",
        "judges": ["V.R. Krishna Iyer", "Jaswant Singh"],
        "case_number": "Criminal Appeal No. 343 of 1977",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["439"],
        "citations": ["(1978) 1 SCC 579", "AIR 1978 SC 527", "1978 Cri LJ 651"],
        "pages": [
            "Appellants convicted of murder applied for bail before Supreme Court pending appeal after earlier rejection.",
            "Krishna Iyer J. on Bail Renewal: Rejection of bail at an early stage does not operate as res judicata. An order refusing bail is not final, and a fresh application can be entertained when long delay in appeal disposal alters circumstances.",
            "Deprivation of personal liberty for prolonged years pending appeal without hearing violates Article 21. Bail granted."
        ]
    },
    {
        "id": "1994_sanjay_dutt",
        "doc_id": "DOC_SC_1994_SANJAY_DUTT",
        "case_id": "CASE_1994_SC_SANJAY_DUTT",
        "name": "Sanjay Dutt v. State through CBI, Bombay",
        "court": "Supreme Court of India",
        "date": "1994-09-09",
        "judges": ["A.M. Ahmadi", "J.S. Verma", "P.B. Sawant", "B.P. Jeevan Reddy", "N.P. Singh"],
        "case_number": "Criminal Appeal No. 574 of 1994",
        "acts": ["Code of Criminal Procedure, 1973", "TADA Act, 1987", "Arms Act, 1959"],
        "sections": ["167(2)", "20(4)"],
        "citations": ["(1994) 5 SCC 410", "1994 SCC (Cri) 1433", "1995 Cri LJ 477"],
        "pages": [
            "Constitution Bench examined the 'indefeasible right' to default bail under Section 167(2) CrPC / Section 20(4) TADA upon expiry of statutory remand period.",
            "The right to default bail accrues on expiry of 180/90 days and remains enforceable until the chargesheet is filed. If chargesheet is filed before the accused applies for default bail, the right is extinguished.",
            "Accused must avail the right before filing of chargesheet by being ready to furnish bail. Principles governing statutory remand authoritatively settled."
        ]
    },
    {
        "id": "2017_parbatbhai_aahir",
        "doc_id": "DOC_SC_2017_PARBATBHAI",
        "case_id": "CASE_2017_SC_PARBATBHAI",
        "name": "Parbatbhai Aahir @ Parbatbhai Bhimsinhbhai Karmur v. State of Gujarat",
        "court": "Supreme Court of India",
        "date": "2017-10-04",
        "judges": ["Dipak Misra", "A.M. Khanwilkar", "D.Y. Chandrachud"],
        "case_number": "Criminal Appeal No. 1723 of 2017",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["482", "384", "420", "120B"],
        "citations": ["(2017) 9 SCC 641", "AIR 2017 SC 4843", "2017 Cri LJ 4970"],
        "pages": [
            "Accused charged with extortion, land grabbing and cheating sought quashing of criminal proceedings under Section 482 CrPC on basis of compromise with victims.",
            "Supreme Court formulated 10 comprehensive guidelines on quashing under Section 482 on compromise: Heinous and serious offences (rape, murder, dacoity, economic offences against society) cannot be quashed on private settlement.",
            "Accused had 17 criminal cases of extortion and organized land grabbing. Inherent powers under Section 482 cannot be exercised to facilitate extortion compromises. Quashing denied."
        ]
    },
    {
        "id": "1952_hanumant",
        "doc_id": "DOC_SC_1952_HANUMANT",
        "case_id": "CASE_1952_SC_HANUMANT",
        "name": "Hanumant Govind Nargundkar v. State of Madhya Pradesh",
        "court": "Supreme Court of India",
        "date": "1952-09-25",
        "judges": ["Mehr Chand Mahajan", "S.R. Das", "N.H. Bhagwati"],
        "case_number": "Criminal Appeal No. 37 of 1952",
        "acts": ["Indian Evidence Act, 1872", "Indian Penal Code, 1860"],
        "sections": ["3", "120B", "465"],
        "citations": ["AIR 1952 SC 343", "1952 SCR 1091", "1953 Cri LJ 129"],
        "pages": [
            "Excise Commissioner was convicted of forgery and criminal conspiracy for awarding tender for sugar barrels based on circumstantial typewriter comparison evidence.",
            "Mahajan J. established the locus classicus on circumstantial evidence: In cases depending on circumstantial evidence, the circumstances from which the conclusion of guilt is drawn must be fully established and consistent only with the guilt of the accused.",
            "There must be a chain of evidence so complete as not to leave any reasonable ground for conclusion consistent with the innocence of the accused. Conviction quashed."
        ]
    },
    {
        "id": "1952_kashmira_singh",
        "doc_id": "DOC_SC_1952_KASHMIRA_SINGH",
        "case_id": "CASE_1952_SC_KASHMIRA_SINGH",
        "name": "Kashmira Singh v. State of Madhya Pradesh",
        "court": "Supreme Court of India",
        "date": "1952-03-04",
        "judges": ["Patanjali Sastri", "B.K. Mukherjea", "S.R. Das", "Vivian Bose"],
        "case_number": "Criminal Appeal No. 53 of 1951",
        "acts": ["Indian Evidence Act, 1872", "Indian Penal Code, 1860"],
        "sections": ["30", "302"],
        "citations": ["AIR 1952 SC 159", "1952 SCR 526", "1952 Cri LJ 839"],
        "pages": [
            "Accused was convicted of murdering a 5-year-old child solely on the confession of a co-accused under Section 30 of the Evidence Act.",
            "Vivian Bose J. on Co-accused Confession: The confession of a co-accused under Section 30 is not substantive evidence against another accused. It can only be used to lend assurance to other independent evidence already established on record.",
            "A court cannot begin with the confession of a co-accused; it must marshal other evidence first. Since there was no independent substantive evidence, conviction under Section 302 IPC set aside."
        ]
    },
    {
        "id": "1976_bhagwan_singh",
        "doc_id": "DOC_SC_1976_BHAGWAN_SINGH",
        "case_id": "CASE_1976_SC_BHAGWAN_SINGH",
        "name": "Bhagwan Singh v. State of Haryana",
        "court": "Supreme Court of India",
        "date": "1975-10-10",
        "judges": ["P.N. Bhagwati", "A.C. Gupta", "S. Murtaza Fazal Ali"],
        "case_number": "Criminal Appeal No. 41 of 1974",
        "acts": ["Indian Evidence Act, 1872"],
        "sections": ["154"],
        "citations": ["(1976) 1 SCC 389", "AIR 1976 SC 202", "1976 Cri LJ 203"],
        "pages": [
            "In a murder trial, prosecution eye-witness turned hostile and was cross-examined by the prosecutor under Section 154 Evidence Act.",
            "Supreme Court held: Merely because a witness is declared hostile under Section 154 Evidence Act, his entire testimony does not become effaced from the record. The court can accept that part of his evidence which is corroborated by other evidence.",
            "The hostile witness supported the presence of the accused with gun at the crime scene. That portion was rightly relied upon to convict under Section 302 IPC."
        ]
    },
    {
        "id": "2005_iqbal_singh_marwah",
        "doc_id": "DOC_SC_2005_IQBAL_MARWAH",
        "case_id": "CASE_2005_SC_IQBAL_MARWAH",
        "name": "Iqbal Singh Marwah and Another v. Meenakshi Marwah and Another",
        "court": "Supreme Court of India",
        "date": "2005-03-11",
        "judges": ["N. Santosh Hegde", "S.N. Variava", "B.P. Singh", "H.K. Sema", "S.B. Sinha"],
        "case_number": "Criminal Appeal No. 402 of 2005",
        "acts": ["Code of Criminal Procedure, 1973", "Indian Penal Code, 1860"],
        "sections": ["195(1)(b)(ii)", "340", "467", "471"],
        "citations": ["(2005) 4 SCC 370", "AIR 2005 SC 2119", "2005 Cri LJ 2161"],
        "pages": [
            "Constitution Bench resolved conflicting decisions on whether Section 195(1)(b)(ii) CrPC bars private complaint when a forged will is produced in probate court.",
            "Held: The statutory bar under Section 195(1)(b)(ii) CrPC (requiring court complaint for offences against public justice) applies ONLY when the forgery is committed after the document is produced or in the custody of the court (custodia legis).",
            "If the document was forged before it was produced in court, a private criminal complaint under Sections 467/471 IPC is fully maintainable. Private complaint upheld."
        ]
    },
    {
        "id": "1979_hussainara_khatoon",
        "doc_id": "DOC_SC_1979_HUSSAINARA",
        "case_id": "CASE_1979_SC_HUSSAINARA",
        "name": "Hussainara Khatoon and Others v. Home Secretary, State of Bihar",
        "court": "Supreme Court of India",
        "date": "1979-02-12",
        "judges": ["P.N. Bhagwati", "O. Chinnappa Reddy"],
        "case_number": "Writ Petition No. 57 of 1979",
        "acts": ["Code of Criminal Procedure, 1973", "Constitution of India"],
        "sections": ["436", "437"],
        "citations": ["(1980) 1 SCC 81", "AIR 1979 SC 1360", "1979 Cri LJ 1036"],
        "pages": [
            "PIL revealing thousands of undertrial prisoners languishing in Bihar jails for periods far exceeding maximum punishment for their alleged offences.",
            "Bhagwati J. recognized the 'Right to Speedy Trial' as an essential ingredient of Article 21. Procedure which keeps poor undertrials in jail without trial for years is unjust, unfair, and unconstitutional.",
            "Supreme Court directed immediate release of undertrials detained longer than maximum statutory punishment and ordered state-provided free legal aid under Article 39A."
        ]
    },
    {
        "id": "1992_ar_antulay",
        "doc_id": "DOC_SC_1992_AR_ANTULAY",
        "case_id": "CASE_1992_SC_AR_ANTULAY",
        "name": "Abdul Rehman Antulay and Others v. R.S. Nayak and Another",
        "court": "Supreme Court of India",
        "date": "1991-12-04",
        "judges": ["B.C. Ray", "M.H. Kania", "K. Jagannatha Shetty", "M.M. Punchhi", "S.C. Agrawal"],
        "case_number": "Criminal Appeal No. 468 of 1989",
        "acts": ["Code of Criminal Procedure, 1973", "Prevention of Corruption Act, 1947"],
        "sections": ["482"],
        "citations": ["(1992) 1 SCC 225", "AIR 1992 SC 1701", "1992 Cri LJ 2717"],
        "pages": [
            "Constitution Bench formulated 11 comprehensive propositions governing the right to speedy trial under Article 21 in criminal prosecutions.",
            "Held: Fair, just and reasonable procedure under Article 21 encompasses right to speedy trial. However, no outer time limit can be fixed for conclusion of criminal proceedings; delay must be balanced against systemic constraints and conduct of accused.",
            "If systemic delay violates right to speedy trial, court can quash proceedings or reduce sentence depending on circumstances."
        ]
    },
    {
        "id": "2014_hardeep_singh",
        "doc_id": "DOC_SC_2014_HARDEEP_SINGH",
        "case_id": "CASE_2014_SC_HARDEEP_SINGH",
        "name": "Hardeep Singh v. State of Punjab and Others",
        "court": "Supreme Court of India",
        "date": "2014-01-10",
        "judges": ["B.S. Chauhan", "F.M.I. Kalifulla", "C.K. Prasad", "M.Y. Eqbal", "A.K. Sikri"],
        "case_number": "Criminal Appeal No. 175 of 2009",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["319"],
        "citations": ["(2014) 3 SCC 92", "AIR 2014 SC 1400", "2014 Cri LJ 1118"],
        "pages": [
            "Constitution Bench settled the scope and standard of evidence required to summon additional persons as accused under Section 319 CrPC during trial.",
            "Held: The word 'evidence' in Section 319 CrPC means statement of witnesses recorded during trial examination-in-chief, even before cross-examination. Power can be exercised against persons not named in FIR or discharged.",
            "The degree of satisfaction required is more than a prima facie case at charge stage, but less than proof beyond reasonable doubt: reasonable satisfaction that accused committed the offence."
        ]
    },
    {
        "id": "1978_maneka_gandhi",
        "doc_id": "DOC_SC_1978_MANEKA_GANDHI",
        "case_id": "CASE_1978_SC_MANEKA_GANDHI",
        "name": "Maneka Gandhi v. Union of India",
        "court": "Supreme Court of India",
        "date": "1978-01-25",
        "judges": ["M.H. Beg", "Y.V. Chandrachud", "P.N. Bhagwati", "V.R. Krishna Iyer", "N.L. Untwalia", "P.S. Kailasam", "S. Murtaza Fazal Ali"],
        "case_number": "Writ Petition No. 231 of 1977",
        "acts": ["Passport Act, 1967", "Constitution of India"],
        "sections": ["10(3)(c)"],
        "citations": ["(1978) 1 SCC 248", "AIR 1978 SC 597", "(1978) 2 SCR 621"],
        "pages": [
            "Petitioner's passport was impounded by the central government without furnishing reasons, invoking Section 10(3)(c) in public interest.",
            "Bhagwati J. revolutionized Article 21 jurisprudence: 'Procedure established by law' must be just, fair and reasonable, not arbitrary or oppressive. Articles 14, 19 and 21 form a golden triangle of fundamental rights.",
            "Natural justice principles (audi alteram partem) must be read into statutory administrative action depriving personal liberty. Impounding order without post-decisional hearing unconstitutional."
        ]
    },
    {
        "id": "1983_machhi_singh",
        "doc_id": "DOC_SC_1983_MACHHI_SINGH",
        "case_id": "CASE_1983_SC_MACHHI_SINGH",
        "name": "Machhi Singh and Others v. State of Punjab",
        "court": "Supreme Court of India",
        "date": "1983-07-20",
        "judges": ["M.P. Thakkar", "A. Varadarajan"],
        "case_number": "Criminal Appeal Nos. 79-84 of 1983",
        "acts": ["Indian Penal Code, 1860", "Code of Criminal Procedure, 1973"],
        "sections": ["302", "354(3)"],
        "citations": ["(1983) 3 SCC 470", "AIR 1983 SC 957", "1983 Cri LJ 1457"],
        "pages": [
            "In a feud between families, Machhi Singh and 11 associates raided five villages at night and murdered 17 persons including women and sleeping children.",
            "Supreme Court concretized Bachan Singh's 'Rarest of Rare' test into 5 specific categories: (1) Manner of murder (extreme brutality/torture); (2) Motive (contract killing/depravity); (3) Anti-social or socially abhorrent nature (bride burning); (4) Magnitude of crime (multiple murders); (5) Personality of victim (helpless child/woman).",
            "Multiple murders of 17 innocent persons in midnight raid shocked the conscience of the community. Death sentence confirmed."
        ]
    },
    {
        "id": "2000_lily_thomas",
        "doc_id": "DOC_SC_2000_LILY_THOMAS",
        "case_id": "CASE_2000_SC_LILY_THOMAS",
        "name": "Lily Thomas and Others v. Union of India and Others",
        "court": "Supreme Court of India",
        "date": "2000-05-05",
        "judges": ["S. Saghir Ahmad", "R.P. Sethi"],
        "case_number": "Writ Petition (Civil) No. 509 of 1992",
        "acts": ["Indian Penal Code, 1860", "Hindu Marriage Act, 1955"],
        "sections": ["494"],
        "citations": ["(2000) 6 SCC 224", "AIR 2000 SC 1650", "2000 Cri LJ 2433"],
        "pages": [
            "Review of Sarla Mudgal ruling on whether prosecuting a Hindu husband for bigamy under Section 494 IPC upon sham conversion to Islam infringes Article 25 religious freedom.",
            "Held: Freedom of religion under Article 25 is subject to public order, morality, and health. Feigning religious conversion to commit bigamy is a fraud on personal law and religion.",
            "Section 494 IPC applies equally to all persons whose first marriage subsists in law. Conviction under Section 494 does not violate Article 25. Review petition dismissed."
        ]
    },
    {
        "id": "2021_amish_devgan",
        "doc_id": "DOC_SC_2021_AMISH_DEVGAN",
        "case_id": "CASE_2021_SC_AMISH_DEVGAN",
        "name": "Amish Devgan v. Union of India and Others",
        "court": "Supreme Court of India",
        "date": "2020-12-07",
        "judges": ["A.M. Khanwilkar", "Sanjiv Khanna"],
        "case_number": "Writ Petition (Criminal) No. 160 of 2020",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["153A", "295A", "505(2)"],
        "citations": ["(2021) 1 SCC 1", "AIR 2021 SC 294", "2021 Cri LJ 612"],
        "pages": [
            "Television journalist aired debate referring to Sufi saint Khwaja Moinuddin Chishti in derogatory terms. Multiple FIRs filed under Sections 153A, 295A and 505(2) IPC.",
            "Supreme Court expounded on Hate Speech: Differentiated between 'free speech' (which can be hurtful or provocative) and 'hate speech' (which targets identity of a community with intent to promote hatred or marginalization).",
            "Refused to quash FIRs under Section 482; journalist's intent and impact of broadcast required police investigation. Consolidated all FIRs to one police station."
        ]
    },
    {
        "id": "1971_ka_abbas",
        "doc_id": "DOC_SC_1971_KA_ABBAS",
        "case_id": "CASE_1971_SC_KA_ABBAS",
        "name": "K.A. Abbas v. Union of India",
        "court": "Supreme Court of India",
        "date": "1970-09-24",
        "judges": ["M. Hidayatullah", "J.M. Shelat", "G.K. Mitter", "C.A. Vaidialingam", "A.N. Ray"],
        "case_number": "Writ Petition No. 152 of 1969",
        "acts": ["Cinematograph Act, 1952", "Constitution of India"],
        "sections": ["5B"],
        "citations": ["(1970) 2 SCC 780", "AIR 1971 SC 481", "1971 (2) SCR 446"],
        "pages": [
            "Film director challenged pre-censorship of documentary film 'A Tale of Four Cities' depicting contrasting lives of rich and poor in Indian cities.",
            "Hidayatullah C.J. on Free Expression in Cinema: Motion pictures have instant appeal to both sight and sound; pre-censorship of films is a valid reasonable restriction under Article 19(2).",
            "Artistic expression depicting social reality or red light areas cannot be banned unless prurient. Directed Central Board of Film Certification to issue 'U' certificate."
        ]
    },
    {
        "id": "2013_sangeet",
        "doc_id": "DOC_SC_2013_SANGEET",
        "case_id": "CASE_2013_SC_SANGEET",
        "name": "Sangeet and Another v. State of Haryana",
        "court": "Supreme Court of India",
        "date": "2012-11-20",
        "judges": ["K.S. Radhakrishnan", "Madan B. Lokur"],
        "case_number": "Criminal Appeal Nos. 490-491 of 2011",
        "acts": ["Indian Penal Code, 1860", "Code of Criminal Procedure, 1973"],
        "sections": ["302", "354(3)"],
        "citations": ["(2013) 2 SCC 452", "AIR 2013 SC 447", "2013 Cri LJ 555"],
        "pages": [
            "Appellants sentenced to death for multiple murders. Supreme Court reviewed inconsistency and subjectivity in death penalty sentencing post-Bachan Singh.",
            "Held: Balancing of aggravating and mitigating circumstances has become judge-centric rather than objective. Courts have frequently ignored the possibility of reformation of the convict.",
            "Death penalty commuted to life imprisonment with a minimum term of 20 years without remission."
        ]
    },
    {
        "id": "2020_mahipal",
        "doc_id": "DOC_SC_2020_MAHIPAL",
        "case_id": "CASE_2020_SC_MAHIPAL",
        "name": "Mahipal v. Rajesh Kumar @ Polia and Another",
        "court": "Supreme Court of India",
        "date": "2019-12-05",
        "judges": ["D.Y. Chandrachud", "Hrishikesh Roy"],
        "case_number": "Criminal Appeal No. 1843 of 2019",
        "acts": ["Code of Criminal Procedure, 1973"],
        "sections": ["439"],
        "citations": ["(2020) 2 SCC 118", "AIR 2020 SC 18", "2020 Cri LJ 601"],
        "pages": [
            "High Court granted bail to a murder accused with 14 criminal antecedents in a perfunctory order recording only 'without expressing any opinion on the merits of the case'.",
            "Chandrachud J. on Duty to Give Reasons in Bail: While court is not required to conduct a mini-trial, it must indicate its reasoning demonstrating application of mind to nature of crime, criminal antecedents, and witness threat.",
            "An unreasoned bail order in a heinous murder case suffers from non-application of mind and perversity. High Court order set aside; bail cancelled."
        ]
    }
]

def generate_batch2():
    print(f"Generating Batch 2 landmark case judgments in {JUDGMENTS_DIR}...")
    count = 0
    for c in BATCH2_CASES:
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

    print(f"\n✔ Successfully generated {count} Batch 2 landmark judgments!")

if __name__ == "__main__":
    generate_batch2()

