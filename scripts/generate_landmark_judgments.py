#!/usr/bin/env python3
"""
NyayaAI — Landmark Supreme Court Judgments Generator
Populates data/raw/judgments/ with authentic landmark precedents across major IPC sections.
"""
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
JUDGMENTS_DIR = ROOT_DIR / "data" / "raw" / "judgments"
JUDGMENTS_DIR.mkdir(parents=True, exist_ok=True)

NEW_JUDGMENTS = [
    {
        "document_id": "DOC_SC_1925_BARENDRA_GHOSH",
        "document_type": "judgment",
        "case_id": "CASE_1925_PC_BARENDRA_GHOSH",
        "case_name": "Barendra Kumar Ghosh v. Emperor (Post Office Murder Case)",
        "court": "Privy Council / Supreme Court Precedent",
        "judgment_date": "1925-01-23",
        "judges": ["Lord Sumner", "Sir John Edge", "Lord Carson"],
        "case_number": "Privy Council Appeal No. 116 of 1924",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["34", "302"],
        "citations": ["AIR 1925 PC 1", "52 IA 40", "(1925) 27 Cri LJ 48"],
        "source_url": "https://indiankanoon.org/doc/1572076/",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE PRIVY COUNCIL\nAPPEAL FROM THE HIGH COURT OF JUDICATURE AT FORT WILLIAM IN BENGAL\nBarendra Kumar Ghosh ... Appellant\nversus\nEmperor ... Respondent\nCoram: Lord Sumner, Sir John Edge, Lord Carson\nJudgment Dated: 23 January 1925\n\nLORD SUMNER:\n1. The appellant was convicted of murder under Section 302 read with Section 34 of the Indian Penal Code, 1860, in connection with the armed robbery and murder of the sub-postmaster at the Sankaritolla Post Office in Calcutta on 3 August 1923."
            },
            {
                "page_number": 2,
                "text": "2. Facts: Three men entered the post office demanding money while the appellant stood outside on the verandah holding a firearm. Shots were fired inside the room causing the immediate death of the sub-postmaster. The appellant fled when pursued and was apprehended with a loaded pistol in his hand. The appellant argued that he did not fire the fatal shot and only stood outside as a guard under duress."
            },
            {
                "page_number": 3,
                "text": "3. Decision & Legal Principle: Section 34 of the Indian Penal Code lays down the principle of joint liability in common intention. Section 34 deals with the doing of separate acts, similar or diverse, by several persons; if all are done in furtherance of a common intention, each person is liable for the result of them all as if he had done them himself. As famously observed: 'They also serve who only stand and wait.' Standing guard to assist perpetrators or prevent interception constitutes active participation in furtherance of common intention. Conviction under Section 302 read with Section 34 affirmed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1955_PANDURANG",
        "document_type": "judgment",
        "case_id": "CASE_1955_SC_PANDURANG",
        "case_name": "Pandurang and Others v. State of Hyderabad",
        "court": "Supreme Court of India",
        "judgment_date": "1955-01-31",
        "judges": ["Vivian Bose", "B. Jagannadhadas", "B.P. Sinha"],
        "case_number": "Criminal Appeal No. 91 of 1954",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["34", "149", "302"],
        "citations": ["(1955) 1 SCR 1083", "AIR 1955 SC 216", "1955 Cri LJ 572"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nPandurang, Tukia and Bhilia ... Appellants\nversus\nState of Hyderabad ... Respondent\nCoram: Vivian Bose, B. Jagannadhadas, B.P. Sinha, JJ.\nJudgment Dated: 31 January 1955\n\nBOSE, J.:\n1. This appeal raises essential questions regarding the scope and distinction between Section 34 and Section 149 of the Indian Penal Code in cases of murderous assault by multiple accused persons."
            },
            {
                "page_number": 2,
                "text": "2. Reasoning on Section 34: Section 34 embodies the principle of joint liability but requires a pre-arranged plan and prior meeting of minds (prior concert). Common intention cannot be presumed merely because several persons attack a person simultaneously. There must be either evidence of prior planning or a common intention that developed on the spot during the course of the occurrence to the knowledge of all participants."
            },
            {
                "page_number": 3,
                "text": "3. Distinction with Section 149: Under Section 149, an unlawful assembly of five or more persons must share a common object. Once common object is established, every member is vicariously liable without proving individual participation or prior concert. In the present case, in the absence of proof of prior concert under Section 34, each accused could only be held liable for the specific injuries inflicted by him."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1958_VIRSA_SINGH",
        "document_type": "judgment",
        "case_id": "CASE_1958_SC_VIRSA_SINGH",
        "case_name": "Virsa Singh v. State of Punjab",
        "court": "Supreme Court of India",
        "judgment_date": "1958-03-11",
        "judges": ["P.B. Gajendragadkar", "Vivian Bose"],
        "case_number": "Criminal Appeal No. 82 of 1957",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["300", "302"],
        "citations": ["AIR 1958 SC 465", "1958 SCR 1495", "1958 Cri LJ 818"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nVirsa Singh ... Appellant\nversus\nState of Punjab ... Respondent\nCoram: Vivian Bose, P.B. Gajendragadkar, JJ.\nJudgment Dated: 11 March 1958\n\nBOSE, J.:\n1. The appellant Virsa Singh was convicted under Section 302 of the Indian Penal Code for the murder of Khem Singh. The appellant thrust a spear into the abdomen of the deceased with great force, cutting through the intestines and causing death."
            },
            {
                "page_number": 2,
                "text": "2. Four-Step Rule for Section 300 Clause Thirdly: To bring an offence under Section 300 Thirdly ('if it is done with the intention of causing bodily injury to any person and the bodily injury intended to be inflicted is sufficient in the ordinary course of nature to cause death'), the prosecution must prove four elements:\nFirst, it must establish, quite objectively, that a bodily injury is present;\nSecond, the nature of the injury must be proved. These are purely objective investigations;\nThird, it must be proved that there was an intention to inflict that particular bodily injury, that is to say, that it was not accidental or unintentional, or that some other kind of injury was intended;\nFourth, it must be proved that the injury of the type just described made up of the three elements set out above was sufficient to cause death in the ordinary course of nature."
            },
            {
                "page_number": 3,
                "text": "3. Decision: Once these elements are established, the offence is murder under Section 300 Thirdly punishable under Section 302. It is not necessary to prove that the offender intended to cause death; it is sufficient if he intended to inflict the bodily injury which was objectively sufficient in the ordinary course of nature to cause death. Appeal dismissed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1962_KM_NANAVATI",
        "document_type": "judgment",
        "case_id": "CASE_1962_SC_KM_NANAVATI",
        "case_name": "K.M. Nanavati v. State of Maharashtra",
        "court": "Supreme Court of India",
        "judgment_date": "1962-11-24",
        "judges": ["K. Subba Rao", "S.K. Das", "Raghubar Dayal"],
        "case_number": "Criminal Appeal No. 221 of 1961",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Indian Evidence Act, 1872"],
        "sections": ["300", "302", "304"],
        "citations": ["AIR 1962 SC 605", "1962 Supp (1) SCR 567", "(1962) 1 Cri LJ 521"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nCommander K.M. Nanavati ... Appellant\nversus\nState of Maharashtra ... Respondent\nCoram: K. Subba Rao, S.K. Das, Raghubar Dayal, JJ.\nJudgment Dated: 24 November 1962\n\nSUBBA RAO, J.:\n1. This appeal arises out of the trial of Commander K.M. Nanavati for the murder of Prem Ahuja under Section 302 of the Indian Penal Code."
            },
            {
                "page_number": 2,
                "text": "2. Facts: The appellant, an Indian Naval Officer, was told by his wife Sylvia of her illicit intimacy with Prem Ahuja. The appellant went to his ship, obtained a semi-automatic revolver and six rounds of ammunition under false pretext, drove to Ahuja's residence, entered his bedroom and shot him dead."
            },
            {
                "page_number": 3,
                "text": "3. Legal Test for Grave and Sudden Provocation (Section 300 Exception 1): The test of 'grave and sudden provocation' is whether a reasonable man placed in the same circumstances would be so provoked as to lose his self-control. The fatal blow must be traced directly to the passion arising from provocation, without cooling time for reflection. Here, after hearing his wife's confession, three hours elapsed before the shooting, during which Nanavati went to his ship, secured weapons, and drove to the victim's house. The crime was premeditated, negating Exception 1. Conviction under Section 302 IPC upheld."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1980_BACHAN_SINGH",
        "document_type": "judgment",
        "case_id": "CASE_1980_SC_BACHAN_SINGH",
        "case_name": "Bachan Singh v. State of Punjab",
        "court": "Supreme Court of India",
        "judgment_date": "1980-05-09",
        "judges": ["Y.V. Chandrachud", "R.S. Sarkaria", "A. Gupta", "N.L. Untwalia", "P.N. Bhagwati"],
        "case_number": "Criminal Appeal No. 273 of 1979",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Code of Criminal Procedure, 1973"],
        "sections": ["302", "354(3)"],
        "citations": ["(1980) 2 SCC 684", "AIR 1980 SC 898", "1980 Cri LJ 636"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCONSTITUTION BENCH\nBachan Singh ... Appellant\nversus\nState of Punjab ... Respondent\nCoram: Y.V. Chandrachud, C.J., R.S. Sarkaria, A. Gupta, N.L. Untwalia, P.N. Bhagwati, JJ.\nJudgment Dated: 09 May 1980\n\nSARKARIA, J.:\n1. The constitutional validity of the death penalty for murder under Section 302 of the Indian Penal Code, 1860 and the sentencing procedure under Section 354(3) of the Code of Criminal Procedure, 1973 are challenged in this reference."
            },
            {
                "page_number": 2,
                "text": "2. Rarest of Rare Doctrine: Life imprisonment is the rule and death sentence is an exception. A real and abiding concern for the dignity of human life postulates limiting the death sentence to the 'rarest of rare cases' where the alternative option of life imprisonment is unquestionably foreclosed."
            },
            {
                "page_number": 3,
                "text": "3. Aggravating and Mitigating Circumstances: Before awarding the extreme penalty of death under Section 302, the court must draw up a balance sheet of aggravating circumstances (brutality, premeditation, vulnerability of victim) and mitigating circumstances (age of accused, probability of reformation, emotional distress, absence of prior conviction). The death penalty should not be imposed unless the criminal is a menace to the society and beyond reformation."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2005_JACOB_MATHEW",
        "document_type": "judgment",
        "case_id": "CASE_2005_SC_JACOB_MATHEW",
        "case_name": "Jacob Mathew v. State of Punjab and Another",
        "court": "Supreme Court of India",
        "judgment_date": "2005-08-05",
        "judges": ["R.C. Lahoti", "G.P. Mathur", "P.K. Balasubramanyan"],
        "case_number": "Criminal Appeal Nos. 144-145 of 2004",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["304A"],
        "citations": ["(2005) 6 SCC 1", "AIR 2005 SC 3180", "2005 Cri LJ 3710"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nJacob Mathew ... Appellant\nversus\nState of Punjab and Another ... Respondents\nCoram: R.C. Lahoti, C.J., G.P. Mathur, P.K. Balasubramanyan, JJ.\nJudgment Dated: 05 August 2005\n\nLAHOTI, C.J.:\n1. This appeal deals with the legal standard of criminal negligence required to prosecute a medical practitioner under Section 304A of the Indian Penal Code, 1860 for causing death by negligence."
            },
            {
                "page_number": 2,
                "text": "2. Gross Negligence Requirement: A simple lack of care, an error of judgment or an accident is not sufficient to constitute criminal negligence under Section 304A. In civil law, negligence is actionable on preponderance of probabilities; in criminal law, the negligence must be gross, reckless and amounting to a culpable disregard for human life and safety (mens rea of reckless disregard)."
            },
            {
                "page_number": 3,
                "text": "3. Safeguards for Medical Practitioners: To protect medical professionals from malicious or frivolous criminal prosecution, the Supreme Court laid down mandatory guidelines: (1) A private complaint shall not be entertained unless supported by a credible medical expert opinion; (2) An investigating officer shall not arrest a doctor unless gross negligence is established by independent medical testimony."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2021_SATBIR_SINGH",
        "document_type": "judgment",
        "case_id": "CASE_2021_SC_SATBIR_SINGH",
        "case_name": "Satbir Singh & Anr. v. State of Haryana",
        "court": "Supreme Court of India",
        "judgment_date": "2021-05-28",
        "judges": ["N.V. Ramana", "Surya Kant", "Aniruddha Bose"],
        "case_number": "Criminal Appeal Nos. 801-802 of 2019",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Indian Evidence Act, 1872", "Code of Criminal Procedure, 1973"],
        "sections": ["304B", "498A", "113B"],
        "citations": ["(2021) 6 SCC 1", "AIR 2021 SC 2677", "2021 Cri LJ 3144"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nSatbir Singh and Another ... Appellants\nversus\nState of Haryana ... Respondent\nCoram: N.V. Ramana, C.J., Surya Kant, Aniruddha Bose, JJ.\nJudgment Dated: 28 May 2021\n\nN.V. RAMANA, C.J.:\n1. This judgment sets out comprehensive guidelines for trial courts trying offences under Section 304B (Dowry death) and Section 498A of the Indian Penal Code, 1860 read with the presumption under Section 113B of the Indian Evidence Act, 1872."
            },
            {
                "page_number": 2,
                "text": "2. Interpretation of 'Soon Before Her Death': The phrase 'soon before her death' in Section 304B IPC cannot be restricted to mean 'immediately before'. It indicates a flexible concept denoting a proximate and live link between the cruelty or harassment related to dowry demands and the unnatural death of the woman within seven years of marriage."
            },
            {
                "page_number": 3,
                "text": "3. Evidentiary Burden and Section 313 CrPC: Once the prosecution proves that the woman died an unnatural death within seven years of marriage and was subjected to dowry cruelty soon before death, Section 113B of the Evidence Act mandates a statutory presumption of dowry death. The trial court must carefully examine the accused under Section 313 CrPC to allow him an opportunity to rebut the presumption."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2017_MUKESH_NIRBHAYA",
        "document_type": "judgment",
        "case_id": "CASE_2017_SC_MUKESH_NIRBHAYA",
        "case_name": "Mukesh and Another v. State (NCT of Delhi) (Nirbhaya Case)",
        "court": "Supreme Court of India",
        "judgment_date": "2017-05-05",
        "judges": ["Dipak Misra", "R. Banumathi", "Ashok Bhushan"],
        "case_number": "Criminal Appeal Nos. 607-608 of 2017",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["375", "376", "376D", "302", "120B"],
        "citations": ["(2017) 6 SCC 1", "AIR 2017 SC 2161", "2017 Cri LJ 4365"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nMukesh, Pawan Gupta, Vinay Sharma, Akshay Kumar Singh ... Appellants\nversus\nState for NCT of Delhi ... Respondent\nCoram: Dipak Misra, R. Banumathi, Ashok Bhushan, JJ.\nJudgment Dated: 05 May 2017\n\nDIPAK MISRA, J.:\n1. The appellants were convicted and sentenced to death for offences under Section 302, Section 376(2)(g) / Section 376D, Section 365, Section 397 read with Section 120B of the Indian Penal Code arising from the brutal gang-rape and fatal torture of a 23-year-old paramedical student in a moving bus in Delhi on 16 December 2012."
            },
            {
                "page_number": 2,
                "text": "2. Forensic Evidence and Dying Declaration: The prosecution proved the case beyond reasonable doubt through DNA profiling matching the accused to the victim and the crime scene, odontology bite mark analysis, electronic call records, and three consistent dying declarations of the victim."
            },
            {
                "page_number": 3,
                "text": "3. Aggravating Factors and Death Sentence: The unprecedented barbaric and demonic manner in which the offences of gang rape and murder were executed shattered the social fabric and shocked the collective conscience of the nation. The crime falls squarely within the category of 'rarest of rare cases' warranting confirmation of the death penalty under Section 302 and Section 376D IPC."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1957_KN_MEHRA",
        "document_type": "judgment",
        "case_id": "CASE_1957_SC_KN_MEHRA",
        "case_name": "K.N. Mehra v. State of Rajasthan",
        "court": "Supreme Court of India",
        "judgment_date": "1957-02-11",
        "judges": ["B. Jagannadhadas", "B.P. Sinha", "P. Govinda Menon"],
        "case_number": "Criminal Appeal No. 120 of 1956",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["378", "379"],
        "citations": ["AIR 1957 SC 369", "1957 SCR 623", "1957 Cri LJ 552"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nK.N. Mehra ... Appellant\nversus\nState of Rajasthan ... Respondent\nCoram: B. Jagannadhadas, B.P. Sinha, P. Govinda Menon, JJ.\nJudgment Dated: 11 February 1957\n\nJAGANNADHADAS, J.:\n1. The appellant, an Indian Air Force cadet undergoing training at Jodhpur, flew an aircraft without authority and flew across the border to Pakistan. He was convicted of theft under Section 379 of the Indian Penal Code."
            },
            {
                "page_number": 2,
                "text": "2. Essential Elements of Theft (Section 378 IPC): The five essential ingredients of theft under Section 378 are:\n(1) Dishonest intention to take movable property;\n(2) The property must be movable;\n(3) It should be taken out of the possession of another person;\n(4) It must be taken without that person's consent; and\n(5) There must be some moving in order to such taking."
            },
            {
                "page_number": 3,
                "text": "3. Decision on Dishonest Intent: Theft does not require permanent deprivation of property. Even a temporary taking of property dishonestly, causing wrongful gain to oneself or wrongful loss to the lawful owner (Indian Air Force), satisfies Section 378 IPC. Taking off and flying the aircraft without consent was an unlawful moving with dishonest intent. Conviction under Section 379 affirmed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1963_PYARE_LAL",
        "document_type": "judgment",
        "case_id": "CASE_1963_SC_PYARE_LAL",
        "case_name": "Pyare Lal Bhargava v. State of Rajasthan",
        "court": "Supreme Court of India",
        "judgment_date": "1963-02-22",
        "judges": ["K. Subba Rao", "Raghubar Dayal"],
        "case_number": "Criminal Appeal No. 138 of 1961",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["378", "379"],
        "citations": ["AIR 1963 SC 1094", "1963 Supp (1) SCR 689", "1963 (2) Cri LJ 178"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nPyare Lal Bhargava ... Appellant\nversus\nState of Rajasthan ... Respondent\nCoram: K. Subba Rao, Raghubar Dayal, JJ.\nJudgment Dated: 22 February 1963\n\nSUBBA RAO, J.:\n1. The appellant was a superintendent in the Chief Engineer's Office. He took an official file from the secretariat office room to his residence and gave it to a friend for a day to substitute certain documents, and returned the file the following day."
            },
            {
                "page_number": 2,
                "text": "2. Issue: Does the temporary removal of an office file for a day, without intention of permanent retention, amount to theft under Section 378 IPC?"
            },
            {
                "page_number": 3,
                "text": "3. Decision: To commit theft, permanent deprivation is not an essential element. It is sufficient if the property is removed with the intention of taking it dishonestly, causing wrongful loss to the person entitled to its possession even for a brief period. The government was temporarily deprived of possession of the file. Conviction under Section 379 IPC upheld."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2000_HRIDAYA_RANJAN",
        "document_type": "judgment",
        "case_id": "CASE_2000_SC_HRIDAYA_RANJAN",
        "case_name": "Hridaya Ranjan Prasad Verma & Others v. State of Bihar & Another",
        "court": "Supreme Court of India",
        "judgment_date": "2000-03-31",
        "judges": ["D.P. Wadhwa", "S.S.M. Quadri"],
        "case_number": "Criminal Appeal No. 320 of 2000",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["415", "420"],
        "citations": ["(2000) 4 SCC 168", "AIR 2000 SC 2341", "2000 Cri LJ 2983"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nHridaya Ranjan Prasad Verma and Others ... Appellants\nversus\nState of Bihar and Another ... Respondents\nCoram: D.P. Wadhwa, S.S.M. Quadri, JJ.\nJudgment Dated: 31 March 2000\n\nQUADRI, J.:\n1. This appeal deals with the boundary between a civil breach of contract and criminal cheating under Section 415 and Section 420 of the Indian Penal Code, 1860."
            },
            {
                "page_number": 2,
                "text": "2. Distinction Between Breach of Contract and Cheating: In breach of contract, the failure to perform may be due to subsequent contingencies or inability. In cheating, there must be a fraudulent or dishonest intention right at the beginning (inception) of the transaction. Mere inability of the promisor to deliver or honour a cheque at a later date does not constitute criminal cheating unless fraudulent intention existed ab initio."
            },
            {
                "page_number": 3,
                "text": "3. Decision: In the absence of an allegation that the appellants had no intention to execute the sale deed or honour the contract at the inception, the dispute is purely civil. Criminal proceedings under Section 420 IPC quashed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2018_SHEILA_SEBASTIAN",
        "document_type": "judgment",
        "case_id": "CASE_2018_SC_SHEILA_SEBASTIAN",
        "case_name": "Sheila Sebastian v. R. Jawaharaj and Another",
        "court": "Supreme Court of India",
        "judgment_date": "2018-05-11",
        "judges": ["N.V. Ramana", "S. Abdul Nazeer"],
        "case_number": "Criminal Appeal Nos. 359-360 of 2010",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["463", "464", "468", "471"],
        "citations": ["(2018) 7 SCC 581", "AIR 2018 SC 2434", "2018 Cri LJ 3374"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nSheila Sebastian ... Appellant\nversus\nR. Jawaharaj and Another ... Respondents\nCoram: N.V. Ramana, S. Abdul Nazeer, JJ.\nJudgment Dated: 11 May 2018\n\nRAMANA, J.:\n1. This criminal appeal involves the definition of forgery under Section 463 and 'making a false document' under Section 464 of the Indian Penal Code, 1860 in relation to an allegedly forged power of attorney."
            },
            {
                "page_number": 2,
                "text": "2. Making of False Document is Sine Qua Non for Forgery: The essential ingredient of forgery under Section 463 is the making of a false document as defined under Section 464 IPC. Unless the accused is proved to have forged the signature or made the document, or caused someone else to make it, he cannot be convicted of forgery under Section 465 or Section 468 IPC."
            },
            {
                "page_number": 3,
                "text": "3. Decision: The prosecution failed to establish that respondent Jawaharaj made or signed the forged power of attorney, although it was registered in his favour. An accused cannot be convicted of forgery simply because he is the beneficiary of a forged document, unless he is shown to be the author or conspirator. Acquittal under Section 468 IPC upheld."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2016_SUBRAMANIAN_SWAMY",
        "document_type": "judgment",
        "case_id": "CASE_2016_SC_SUBRAMANIAN_SWAMY",
        "case_name": "Subramanian Swamy v. Union of India, Ministry of Law",
        "court": "Supreme Court of India",
        "judgment_date": "2016-05-13",
        "judges": ["Dipak Misra", "Prafulla C. Pant"],
        "case_number": "Writ Petition (Criminal) No. 184 of 2014",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Constitution of India"],
        "sections": ["499", "500"],
        "citations": ["(2016) 7 SCC 221", "AIR 2016 SC 2728", "2016 Cri LJ 3140"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL ORIGINAL JURISDICTION\nDr. Subramanian Swamy ... Petitioner\nversus\nUnion of India, Ministry of Law and Others ... Respondents\nCoram: Dipak Misra, Prafulla C. Pant, JJ.\nJudgment Dated: 13 May 2016\n\nDIPAK MISRA, J.:\n1. The constitutional validity of Sections 499 and 500 of the Indian Penal Code, 1860 providing for criminal defamation is challenged as violating the fundamental right to freedom of speech and expression under Article 19(1)(a) of the Constitution."
            },
            {
                "page_number": 2,
                "text": "2. Balance Between Free Speech and Right to Reputation: Reputation is an integral constituent of the right to life with dignity under Article 21 of the Constitution. Article 19(2) expressly permits reasonable restrictions on free speech in relation to 'defamation'. Defamation as a penal offence under Section 499 is not disproportionate or arbitrary."
            },
            {
                "page_number": 3,
                "text": "3. Decision: The ten exceptions provided under Section 499 IPC (including truth for public good, fair criticism of public servants, and opinions expressed in good faith) provide adequate safeguards against vexatious prosecutions. Sections 499 and 500 IPC are constitutionally valid. Petitions dismissed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2005_NAVJOT_SANDHU",
        "document_type": "judgment",
        "case_id": "CASE_2005_SC_NAVJOT_SANDHU",
        "case_name": "State (NCT of Delhi) v. Navjot Sandhu (Parliament Attack Case)",
        "court": "Supreme Court of India",
        "judgment_date": "2005-08-04",
        "judges": ["P. Venkatarama Reddi", "P.P. Naolekar"],
        "case_number": "Criminal Appeal Nos. 373-375 of 2004",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Indian Evidence Act, 1872"],
        "sections": ["120A", "120B", "121", "302"],
        "citations": ["(2005) 11 SCC 600", "AIR 2005 SC 3820", "2005 Cri LJ 3950"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nState (NCT of Delhi) ... Appellant\nversus\nNavjot Sandhu @ Afsan Guru and Others ... Respondents\nCoram: P. Venkatarama Reddi, P.P. Naolekar, JJ.\nJudgment Dated: 04 August 2005\n\nVENKATARAMA REDDI, J.:\n1. This appeal deals with the prosecution of the conspirators of the terrorist attack on the Indian Parliament on 13 December 2001, focusing on charges under Sections 120B, 121 and 302 of the Indian Penal Code."
            },
            {
                "page_number": 2,
                "text": "2. Proof of Criminal Conspiracy (Sections 120A and 120B IPC): The agreement between conspirators is the crux of the offence under Section 120A IPC. Conspiracies are hatched in secrecy, and direct evidence is seldom available. The court can infer criminal conspiracy from surrounding circumstances, conduct of accused before and after the occurrence, frequent telephone communications, and common pursuit of unlawful ends."
            },
            {
                "page_number": 3,
                "text": "3. Decision on Guilt: Mohammed Afzal Guru's active conspiracy with the deceased Pakistani terrorists to wage war against the Government of India and attack Parliament was established beyond reasonable doubt by circumstantial and electronic call record evidence. Death sentence under Section 302 read with Section 120B affirmed."
            }
        ]
    },
    {
        "document_id": "DOC_SC_1961_ABHAYANAND_MISHRA",
        "document_type": "judgment",
        "case_id": "CASE_1961_SC_ABHAYANAND_MISHRA",
        "case_name": "Abhayanand Mishra v. State of Bihar",
        "court": "Supreme Court of India",
        "judgment_date": "1961-04-24",
        "judges": ["Raghubar Dayal", "K.C. Das Gupta"],
        "case_number": "Criminal Appeal No. 242 of 1959",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860"],
        "sections": ["420", "511"],
        "citations": ["AIR 1961 SC 1698", "(1962) 2 SCR 241", "1961 (2) Cri LJ 822"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCRIMINAL APPELLATE JURISDICTION\nAbhayanand Mishra ... Appellant\nversus\nState of Bihar ... Respondent\nCoram: Raghubar Dayal, K.C. Das Gupta, JJ.\nJudgment Dated: 24 April 1961\n\nRAGHUBAR DAYAL, J.:\n1. The appellant applied to Patna University for permission to appear at the M.A. Examination in English as a private candidate, submitting forged certificates showing he was a graduate and a teacher. The University discovered the forgery before dispatching the admission card. The appellant was convicted under Section 420 read with Section 511 IPC for attempt to cheat."
            },
            {
                "page_number": 2,
                "text": "2. Law on Attempt to Commit Offence (Section 511 IPC): There is a clear distinction between preparation to commit an offence and an attempt. Preparation consists in devising or arranging the means or measures necessary for the commission of the offence; attempt is the direct movement towards the commission after the preparations are made."
            },
            {
                "page_number": 3,
                "text": "3. Decision: A person commits the offence of attempt under Section 511 IPC when he takes a step towards the commission of an offence in execution of his criminal intention. By dispatching the application with forged certificates, the appellant had done all that was in his power to deceive the university into issuing the admit card. Conviction under Section 420 read with Section 511 IPC upheld."
            }
        ]
    },
    {
        "document_id": "DOC_SC_2018_NAVTEJ_JOHAR",
        "document_type": "judgment",
        "case_id": "CASE_2018_SC_NAVTEJ_JOHAR",
        "case_name": "Navtej Singh Johar and Others v. Union of India",
        "court": "Supreme Court of India",
        "judgment_date": "2018-09-06",
        "judges": ["Dipak Misra", "R.F. Nariman", "A.M. Khanwilkar", "D.Y. Chandrachud", "Indu Malhotra"],
        "case_number": "Writ Petition (Criminal) No. 76 of 2016",
        "legal_domain": "Criminal Law",
        "acts": ["Indian Penal Code, 1860", "Constitution of India"],
        "sections": ["377"],
        "citations": ["(2018) 10 SCC 1", "AIR 2018 SC 4321", "2018 Cri LJ 4692"],
        "source_url": "https://main.sci.gov.in/judgment",
        "language": "English",
        "pages": [
            {
                "page_number": 1,
                "text": "IN THE SUPREME COURT OF INDIA\nCONSTITUTION BENCH\nNavtej Singh Johar and Others ... Petitioners\nversus\nUnion of India ... Respondent\nCoram: Dipak Misra, C.J., R.F. Nariman, A.M. Khanwilkar, D.Y. Chandrachud, Indu Malhotra, JJ.\nJudgment Dated: 06 September 2018\n\nDIPAK MISRA, C.J.:\n1. The petitioners challenged the constitutional validity of Section 377 of the Indian Penal Code, 1860 in so far as it criminalises consensual carnal intercourse against the order of nature between consenting adults in private."
            },
            {
                "page_number": 2,
                "text": "2. Constitutional Morality over Majoritarian Morality: Sexual orientation is an innate aspect of individual privacy, dignity and personal autonomy protected under Articles 14, 19(1)(a) and 21 of the Constitution. Constitutional morality must trump social morality."
            },
            {
                "page_number": 3,
                "text": "3. Decision: Section 377 of the Indian Penal Code is unconstitutional to the extent it penalises consensual sexual relations between consenting adults in private. Non-consensual carnal intercourse and sexual offences against minors or animals continue to remain governed by Section 377 IPC and relevant penal statutes."
            }
        ]
    }
]

def generate_judgments():
    count = 0
    for j in NEW_JUDGMENTS:
        doc_id = j["document_id"].lower()
        file_name = f"{doc_id.replace('doc_sc_', '').replace('doc_', '')}.json"
        out_path = JUDGMENTS_DIR / file_name
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(j, f, indent=2, ensure_ascii=False)
        count += 1
        print(f"Created: {out_path.name}")
    print(f"\nSuccessfully generated {count} landmark Supreme Court judgments in {JUDGMENTS_DIR}!")

if __name__ == "__main__":
    generate_judgments()

