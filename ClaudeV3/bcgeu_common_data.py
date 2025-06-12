# Coast Mountain College Common Agreement Data
# Complete data structure containing all articles, appendices, definitions, and metadata
# Based on the Common Agreement between The Employers' Bargaining Committee and BCGEU

AGREEMENT_DATA = {
    "metadata": {
        "title": "Common Agreement between The Employers' Bargaining Committee and B.C. General Employees' Union (BCGEU)",
        "parties": {
            "employers": "The Employers' Bargaining Committee on behalf of Member Institutions",
            "union": "B.C. General Employees' Union (BCGEU)",
            "member_institutions": [
                "Camosun College",
                "Coast Mountain College", 
                "Northern Lights College",
                "Okanagan College",
                "Selkirk College"
            ],
            "local_unions": [
                "BCGEU Local 701 (Camosun College)",
                "BCGEU Local 707 (Okanagan College)", 
                "BCGEU Local 709 (Selkirk College)",
                "BCGEU Local 710 (Northern Lights College)",
                "BCGEU Local 712 (Coast Mountain College)"
            ]
        },
        "effective_period": "April 1, 2022 to March 31, 2025",
        "document_version": "04/2025",
        "total_articles": 17,
        "total_appendices": 8
    },
    
    "definitions": {
        "agreement": "This Common Agreement reached between the employers and the local unions as defined in 'Parties' or 'Common Parties'.",
        "collective_agreement": "The combination of provisions of the Common Agreement with local provisions that constitute a Collective Agreement between an institution and a local union.",
        "employee": "A person employed within a bargaining unit represented by the BCGEU that has ratified a Collective Agreement that includes this Common Agreement.",
        "employer": "An employer that has ratified a Collective Agreement that includes this Common Agreement.",
        "institution": "A post-secondary institution that has ratified a Collective Agreement that includes this Common Agreement.",
        "jadrc": "The Joint Administration and Dispute Resolution Committee established pursuant to Clause 3.2.",
        "joint_labour_management_committee": "A committee formed by local parties with equal representation from a local union and an institution.",
        "local_parties": "The institution and local bargaining unit where both have ratified a Collective Agreement that includes this Common Agreement.",
        "local_provision": "A provision of a Collective Agreement established by negotiations between an individual employer and a local union.",
        "local_union": "A bargaining unit representing employees at an institution that has ratified a Collective Agreement that includes this Common Agreement.",
        "ministry": "The Ministry of Advanced Education, Skills and Training.",
        "psea": "The Post-Secondary Employers' Association that is established for post-secondary institutions under the Public Sector Employers' Act.",
        "ratification": "The acceptance by the BCGEU and by both an institution and the PSEA of the terms of a Collective Agreement that includes this Common Agreement.",
        "union": "The B.C. General Employees Union (BCGEU)."
    },
    
    "articles": {
        "1": {
            "title": "PREAMBLE",
            "sections": {
                "1.1": {
                    "title": "Purpose of Common Agreement",
                    "subsections": {
                        "1.1.1": "The purpose of the Common Agreement is to establish and maintain orderly collective bargaining procedures and to set forth the terms and conditions of employment.",
                        "1.1.2": "The Parties share a desire to improve the quality of educational service provided by the Institution and are determined to establish a harmonious and effective working relationship at all levels of the Institution in which members of the bargaining unit are employed."
                    }
                },
                "1.2": {
                    "title": "Future Legislation",
                    "content": "In the event that any future legislation renders null and void or materially alters any provision of the Common Agreement, the Parties will negotiate a mutually agreeable amended provision."
                },
                "1.3": {
                    "title": "Conflict with Policies and Regulations",
                    "content": "Every reasonable effort will be made to harmonize employer policies and regulations with the provisions of the Common Agreement. In the event of a conflict between the contents of the Common Agreement and any policies and regulations made by the Employer, the terms of the Common Agreement will prevail."
                },
                "1.4": {
                    "title": "Singular and Plural",
                    "content": "Wherever the singular is used in the Common Agreement, the same shall be construed as meaning the plural if the context requires unless otherwise specifically stated."
                }
            }
        },
        "2": {
            "title": "HARASSMENT",
            "sections": {
                "2.1": {
                    "title": "Statement of Commitment",
                    "content": "The Institutions promote teaching, scholarship and research and the free and critical discussion of ideas. Unions and employers are committed to providing a working and learning environment that allows for full and free participation of all members of the institutional community. Harassment undermines these objectives and violates the fundamental rights, personal dignity and integrity of individuals or groups of individuals."
                },
                "2.2": {
                    "title": "Definitions",
                    "subsections": {
                        "2.2.1": {
                            "title": "Harassment",
                            "definition": "A form of discrimination that adversely affects the recipient on one or more of the prohibited grounds under the BC Human Rights Code. Harassment is behaviour or the effect of behaviour, whether direct or indirect, which meets one of the following conditions: (a) is abusive or demeaning; (b) would be viewed by a reasonable person experiencing the behaviour as an interference with their participation in an institutional related activity; (c) creates a poisoned environment.",
                            "protected_grounds": [
                                "race", "colour", "ancestry", "place of origin", "political belief", "religion", 
                                "marital status", "family status", "physical or mental disability", "sex", 
                                "sexual orientation", "gender identity or expression", "age"
                            ]
                        },
                        "2.2.2": {
                            "title": "Sexual Harassment",
                            "definition": "Behaviour of a sexual nature by a person who knows or ought reasonably to know that the behaviour is unwanted or unwelcome and which interferes with another person's participation in an institution-related activity; or leads to or implies employment, or academically-related consequences for the person harassed; or which creates a poisoned environment."
                        }
                    }
                },
                "2.3": {
                    "title": "Procedures",
                    "subsections": {
                        "2.3.1": {
                            "title": "Local Informal Processes",
                            "content": "The Parties agree that the local parties where mutually agreeable, may first attempt to use local policies or processes to resolve complaints of harassment and sexual harassment prior to accessing mediation and investigation procedures."
                        },
                        "2.3.2": {
                            "title": "Right to Legal Counsel",
                            "content": "The Union is the exclusive bargaining agent for the bargaining unit employee and as such has the exclusive right to represent the employee in all matters pertaining to their terms and conditions of employment. An individual bargaining unit employee has no right to be represented by legal counsel during an Article 2 investigation involving an allegation of harassment."
                        },
                        "2.3.3": {
                            "title": "Mediation",
                            "process": [
                                "Local parties will discuss the nature of the complaint and agree upon who will conduct the mediation",
                                "The mediation process and resolution will be kept strictly confidential by all participants",
                                "Where a resolution is reached, the complainant and the respondent must agree in writing to the resolution",
                                "No record of the mediation except the written agreed resolution will be placed on an employee's file",
                                "The written resolution will be removed from the employee's file after 12 months unless there has been a subsequent complaint"
                            ]
                        },
                        "2.3.4": {
                            "title": "Investigation",
                            "content": "Where either the complainant or respondent does not agree to mediation, or no resolution is reached during the mediation, the complaint will be referred to an investigator selected from the list of investigators in Appendix B. An investigator will be appointed within 10 working days of referral."
                        }
                    }
                }
            }
        },
        "3": {
            "title": "EMPLOYER/UNION RELATIONS",
            "sections": {
                "3.1": {
                    "title": "Human Resources Database",
                    "content": "The Parties believe that their ongoing and collective bargaining relationships are enhanced through useful, timely, and accessible data on relevant human resources matters.",
                    "relevant_matters": {
                        "health_and_welfare": ["Benefit Plan Designs", "Participation rates", "Premiums", "Cost sharing", "Commission costs", "Carrier contracts"],
                        "collective_bargaining": ["Salary information by classification", "FTE, headcount, placement on scale, appointment status", "Demographics: age and gender"],
                        "contract_administration": ["Arbitration, Labour Relations Board, JADRC, Harassment, Jurisdictional and other third-party decisions and costs", "Local Letters of Understanding"]
                    }
                },
                "3.2": {
                    "title": "Joint Administration and Dispute Resolution Committee",
                    "subsections": {
                        "3.2.1": {
                            "title": "Formation and Composition",
                            "content": "The Parties to this agreement will maintain a Joint Administration and Dispute Resolution Committee (JADRC) consisting of three representatives of the Employers and three representatives of the BCGEU."
                        },
                        "3.2.2": {
                            "title": "Operation",
                            "content": "Meetings of JADRC shall be held as needed. A meeting shall be held within 20 days of the written request of either Party unless mutually agreed otherwise. A minimum of four representatives with equal representation from the Common Parties will constitute a quorum."
                        },
                        "3.2.3": {
                            "title": "Purpose",
                            "purposes": [
                                "Assist in the administration of the Common Agreement",
                                "Provide a forum for dialogue between the Parties respecting sectoral issues impacting labour relations",
                                "Provide a means for resolving issues pertaining to the implementation, interpretation and resolution of matters arising from the Common Agreement",
                                "Appoint arbitrator(s) as applicable for Common Agreement Dispute Resolution",
                                "Develop strategies to reduce arbitration and related costs"
                            ]
                        }
                    }
                },
                "3.3": {
                    "title": "Expedited Arbitration",
                    "subsections": {
                        "3.3.1": {
                            "title": "Expedited Arbitrations",
                            "content": "Where a difference arises at an institution relating to the interpretation, application or administration of a local agreement, either of the local parties may notify the other local party of its desire to arbitrate and to submit the difference to expedited arbitration before a single arbitrator."
                        },
                        "3.3.2": {
                            "title": "Issues for Expedited Arbitration",
                            "excluded_grievances": [
                                "Dismissals",
                                "Suspensions in excess of five working days", 
                                "Policy grievances",
                                "Grievances requiring substantial interpretation of a provision of the Collective Agreement",
                                "Grievances requiring the presentation of extrinsic evidence",
                                "Grievances where a local party intends to raise a preliminary objection",
                                "Grievances arising from the duty to accommodate",
                                "Grievances arising from the interpretation, application and administration of the Common Agreement"
                            ]
                        },
                        "3.3.3": {
                            "title": "Expedited Arbitrators",
                            "arbitrators": [
                                "Chris Sullivan", "Mark Brown", "Corrin Bell", "Julie Nichols", 
                                "Alison Matacheskie", "Komi Kandola", "Randy Noonan"
                            ]
                        }
                    }
                },
                "3.4": {
                    "title": "Leave of Absence for College Committees and Union Leave",
                    "subsections": {
                        "3.4.1": {
                            "title": "Leave of Absence for College Committees",
                            "content": "An employee whose assigned work schedule would prevent them from attending meetings of a college committee to which they have been elected or appointed, will be granted a leave of absence from their regular duties without loss of pay or other entitlements."
                        },
                        "3.4.2": {
                            "title": "Union Leave",
                            "content": "The Employer will grant a leave of absence without loss of pay or other entitlements for the purpose of attending meetings to the total equivalent of one-quarter full-time equivalent per annum."
                        }
                    }
                }
            }
        },
        "4": {
            "title": "PRIOR LEARNING ASSESSMENT",
            "sections": {
                "4.1": {
                    "title": "Definition",
                    "content": "Prior Learning Assessment (PLA) is the assessment by some valid and reliable means, of what has been learned through formal and non-formal education/training or experience, that is worthy of credit in a course or program offered by the institution providing credit."
                },
                "4.2": {
                    "title": "Prior Learning Assessment as Workload",
                    "content": "Prior learning assessment work undertaken by an employee covered by this Agreement will be integrated into and form part of the employee's workload as workload is defined in the employee's Collective Agreement."
                },
                "4.3": {
                    "title": "Training in Prior Learning Assessment",
                    "content": "An employee required to perform prior learning assessment responsibilities as part of their workload, has a right to employer-paid training time and expenses, in the methodology and application of prior learning assessment as necessary for the assigned task."
                },
                "4.4": {
                    "title": "Prior Learning Assessment Coordinators",
                    "content": "Prior Learning Assessment coordinators will be instructor or instructional bargaining unit members."
                }
            }
        },
        "5": {
            "title": "COPYRIGHT AND INTELLECTUAL PROPERTY",
            "sections": {
                "5.1": {
                    "title": "Copyright Ownership",
                    "subsections": {
                        "5.1.1": "The copyright belongs to the employee(s) where the work product has been prepared or created as part of assigned duties, other than the duties listed in Clause 5.1.2, and the copyright to all copyrightable material shall be the sole property of the employee(s).",
                        "5.1.2": {
                            "title": "Institution Ownership",
                            "conditions": [
                                "Employee has been hired or agrees to create and produce copyrightable work product for the institution",
                                "Employee is given release time from usual duties to create and produce copyrightable work product",
                                "Employee is paid, in addition to their regular rate of pay, for their time in an appointment to produce copyrightable work product"
                            ]
                        }
                    }
                },
                "5.2": {
                    "title": "Employer Rights to Materials Copyrighted by Employee(s)",
                    "content": "Where the employee holds the copyright pursuant to Clause 5.1.1, the institution shall have a right to use their copyrighted material in perpetuity for institutional purposes. The institution may amend and update the copyrighted material with the approval of the employee(s) holding the copyright to the material."
                },
                "5.3": {
                    "title": "Employee Rights to Materials Copyrighted by the Employer",
                    "content": "Where the institution holds the copyright pursuant to Clause 5.1.2, the employee(s) shall have the right to use in perpetuity, free of charge, such copyrighted material."
                }
            }
        },
        "6": {
            "title": "JOB SECURITY",
            "sections": {
                "6.1": {
                    "title": "Employee Security and Regularization",
                    "subsections": {
                        "6.1.1": {
                            "title": "Intent",
                            "content": "The purpose of this Article is to ensure that provisions relating to employee security and regularization of employees are established within each Collective Agreement affecting employees covered by this Agreement."
                        },
                        "6.1.2": {
                            "title": "Definitions",
                            "definitions": {
                                "department_or_functional_area": "The operational or administrative sub-division of an institution within which an employee is appointed and assigned workload and may include geographic limitations.",
                                "employee_security": "The array of entitlements to continued employment, health and welfare and other benefits, and other rights available to employees through this Agreement or a local Collective Agreement.",
                                "non_regular_employee": "A person employed on any basis other than regular as defined in the local Collective Agreement.",
                                "regularization": "The process by which a non-regular employee converts to regular status under this Article.",
                                "regular_full_time": "A person who holds an appointment to ongoing work with a full-time annual workload within one or more departments or functional areas.",
                                "regular_part_time": "A person who holds an appointment to an ongoing annual workload of less than full-time within one or more departments or functional areas."
                            }
                        },
                        "6.1.3": {
                            "title": "Parameters for Employee Security and Regularization",
                            "regularization_criteria": [
                                "Entitlement to regularization after a period of time worked of at least two consecutive appointment years of work at a workload of 50% or greater for each of two consecutive appointment years and where there is a reasonable expectation of ongoing employment",
                                "OR entitlement to regularization after the employee has performed a workload at least 120% of an annualized workload over at least two consecutive years and there is a reasonable expectation of an ongoing workload assignment"
                            ]
                        }
                    }
                },
                "6.2": {
                    "title": "Program Transfers and Mergers",
                    "subsections": {
                        "6.2.1": {
                            "title": "Notice of Program Transfer / Merger",
                            "content": "When one or more institutions covered by this Agreement decides to transfer or merge a program or a partial program and the transfer or merger will result in the transfer or layoff of one or more employees, the institutions will provide written notice to the local union(s) as soon as possible, but in no event less than 60 days prior to the date of transfer or merger."
                        }
                    }
                },
                "6.3": {
                    "title": "Registry of Laid Off Employees",
                    "subsections": {
                        "6.3.1": {
                            "title": "Electronic Posting of Available Positions",
                            "content": "On behalf of the Parties, the PSEA will maintain a system-wide electronic Registry of job postings and the necessary supporting database. Institutions will post on the Registry all employment opportunities of half-time or more and longer than three months in duration."
                        },
                        "6.3.2": {
                            "title": "Electronic Registry of Eligible Employees (Registrants)",
                            "eligibility": [
                                "Regular employees with one calendar year of service working at 50% workload or greater",
                                "Non-regular employees with two calendar years of service working at 50% workload or greater"
                            ]
                        }
                    }
                },
                "6.4": {
                    "title": "Targeted Labour Adjustment",
                    "subsections": {
                        "6.4.1": {
                            "title": "Employer Commitments",
                            "content": "It is agreed that the institution will make every reasonable attempt to minimize the impact of funding shortfalls and reductions on the workforce."
                        },
                        "6.4.2": {
                            "title": "Menu of Labour Adjustment Strategies",
                            "workplace_organization": [
                                "Job sharing",
                                "Reduced hours of work through partial leaves",
                                "Transfers to other areas within the bargaining unit",
                                "Unpaid leaves of absence",
                                "Workload averaging that does not incur a net increase in compensation cost",
                                "Combined pension earnings and reduced workload to equal 100% of regular salary",
                                "Agreed secondment"
                            ],
                            "employee_transition": [
                                "Paid leaves of absence",
                                "Severance with up to 12 months' severance payment",
                                "Workload averaging that does incur a net increase in compensation",
                                "Purchasing past pensionable service",
                                "Early retirement incentives",
                                "Retraining",
                                "Continuation of health and welfare benefits"
                            ]
                        }
                    }
                },
                "6.5": {
                    "title": "Contracting Out",
                    "content": "An institution covered by the Common Agreement will not contract out any work presently performed by the employees covered by the Common Agreement which would result in the layoff of such employees, or the instructional activities that are contained in the programs listed and/or funded in the approved annual institutional program profile."
                },
                "6.6": {
                    "title": "Education Technology/ Distributed Learning",
                    "provisions": [
                        "Distributed learning includes print based education courses, online or web-based instruction, video-conferencing, teleconferencing, instructional video and audio tapes, hybrid or mixed-mode programs and courses",
                        "The Employer will plan in collaboration with the department or functional area and the employee(s) who will develop and/or deliver the program or course",
                        "The Employer will provide the necessary technological and human resources for employees assigned to develop and deliver the program and courses",
                        "Employees shall not be required to deliver distributed learning programs/courses from their home",
                        "No regular employee will be laid off as a direct result of the introduction of distributed learning or education technology"
                    ]
                }
            }
        },
        "7": {
            "title": "LEAVES",
            "sections": {
                "7.1": {
                    "title": "Definitions",
                    "content": "All references to spouse within the leave provisions include, heterosexual, common-law and same sex partners. References to family include spouse, children, children's spouses, stepchild, stepchild in-law, siblings, in-law siblings, parents, step-parents, parents-in-law, grandparents, grandchildren, nieces and nephews, and any other person living in the same household who is dependent upon the employee."
                },
                "7.2": {
                    "title": "General Leave",
                    "content": "An Employer may grant a leave of absence with or without pay to an employee for any reason for up to 24 consecutive months. Such leaves shall not be unreasonably denied."
                },
                "7.6": {
                    "title": "Bereavement Leave",
                    "content": "An employee will be entitled to five days leave with no loss of pay and benefits in the case of the death of a family member and upon notification to the Employer."
                },
                "7.7": {
                    "title": "Family Illness Leave",
                    "content": "An employee will be granted leave of absence for up to five days per year without loss of pay or benefits for family illness."
                },
                "7.8": {
                    "title": "Compassionate Care Leave",
                    "subsections": {
                        "7.8.1": {
                            "title": "Entitlement",
                            "content": "An employee will be granted a compassionate care leave of absence without pay for up to 27 weeks to care for a gravely ill family member. The employee must provide a medical certificate as proof that the ill family member needs care or support and is at risk of dying within 26 weeks."
                        }
                    }
                },
                "7.11": {
                    "title": "Public Duties",
                    "subsections": {
                        "7.11.1": "An employer may grant a leave of absence without pay to an employee to engage in election campaign activities in a municipal, provincial, federal election, or Indigenous government to a maximum of 90 days.",
                        "7.11.2": "An employer will grant a leave of absence without pay to an employee to seek election or where elected to public office, for up to two consecutive terms."
                    }
                },
                "7.16": {
                    "title": "Leave for Domestic Violence",
                    "entitlements": [
                        "Up to five days of paid leave",
                        "Up to five days of unpaid leave", 
                        "Up to 15 weeks of additional unpaid leave"
                    ]
                },
                "7.17": {
                    "title": "Cultural Leave for Indigenous Employees",
                    "content": "A self-identified Indigenous employee may request up to two days' leave with pay per calendar year to organize and/or attend Indigenous cultural event(s). Such leave will not be unreasonably withheld."
                }
            }
        },
        "8": {
            "title": "PARENTAL LEAVE",
            "sections": {
                "8.1": {
                    "title": "Preamble",
                    "subsections": {
                        "8.1.1": {
                            "title": "Definitions",
                            "definitions": {
                                "common_law_partner": "A person of the same or different sex where the employee has signed a declaration or affidavit that they have been living in a common-law relationship or have been co-habiting for at least 12 months.",
                                "base_salary": "The salary that an employee would earn if working their full workload up to a maximum of a full workload as defined in the employee's Collective Agreement."
                            }
                        },
                        "8.1.2": {
                            "title": "Entitlement",
                            "content": "Upon written request, an employee shall be entitled to a leave of absence without pay of up to six consecutive months in addition to statutory requirements."
                        }
                    }
                },
                "8.5": {
                    "title": "Supplemental Employment Benefit for Maternity and Parental Leave",
                    "subsections": {
                        "8.5.1": {
                            "title": "Benefits",
                            "benefits": {
                                "first_week": "100% of their salary calculated on their average base salary",
                                "maternity_leave": "For a maximum of 15 additional weeks, the difference between EI benefits and 95% of their salary",
                                "parental_leave_standard": "For up to a maximum of 35 weeks, the difference between EI Standard Parental Benefits and 85% of salary",
                                "parental_leave_extended": "For a maximum of 61 weeks, the same total SEB benefit amount as 35 week option, spread out over 61-week period",
                                "last_week": "100% of their salary calculated on their average base salary"
                            }
                        }
                    }
                }
            }
        },
        "9": {
            "title": "HEALTH AND WELFARE BENEFITS",
            "sections": {
                "9.1": {
                    "title": "Joint Committee on Benefits Administration",
                    "subsections": {
                        "9.1.1": {
                            "title": "Committee Established",
                            "content": "The Parties agree to maintain a Joint Committee on Benefits with four members appointed by each side. Two union representatives will represent the BCGEU on this Committee."
                        },
                        "9.1.2": {
                            "title": "Committee Mandate",
                            "mandate": [
                                "Comparison and analysis of contract administration and costs",
                                "Monitoring carrier performance including receiving reports from the plan administrator(s)",
                                "Reviewing the cost effectiveness and quality of benefit delivery, service, and administration by carriers",
                                "Tendering of contracts",
                                "Training for local Joint Rehabilitation Committees"
                            ]
                        }
                    }
                },
                "9.2": {
                    "title": "Specific Benefits",
                    "subsections": {
                        "9.2.1": {
                            "title": "Benefit Provisions",
                            "benefits": {
                                "basic_medical": "Basic Medical Insurance under the British Columbia Medical Plan, subject to Plan provisions",
                                "extended_health": {
                                    "lifetime_coverage": "Unlimited",
                                    "reimbursement_level": "95%",
                                    "hearing_aid": "$1500 every four years (effective April 1, 2023)",
                                    "eye_vision_exams": "$100 every two years",
                                    "professional_services": "$25 per visit maximum for the first three visits per calendar year (effective April 1, 2023)"
                                },
                                "group_life": "Three times the employee's annual salary",
                                "dental_plan": "Plan A that includes revision of cleaning of the teeth (prophylaxis and scaling) every nine months except dependent children (up to age 19) and those with gum disease and other dental problems"
                            }
                        }
                    }
                },
                "9.3": {
                    "title": "Disability Benefits",
                    "subsections": {
                        "9.3.2": {
                            "title": "Plan Elements",
                            "elements": [
                                "Benefit level of sick leave at 100% for the first 30 calendar days",
                                "Short-term disability at 70% weekly indemnity for the next 21 weeks",
                                "Long-term disability leave of 70% thereafter",
                                "Long-term disability as defined on the basis of two-year own occupation and any other occupation thereafter",
                                "Health and welfare benefit premiums paid by the Employer or the Plan for employees on sick leave, short-term disability and long-term disability",
                                "Employer payment of premiums for both short-term and long-term disability benefits"
                            ]
                        }
                    }
                }
            }
        },
        "10": {
            "title": "PENSIONS",
            "sections": {
                "10.1": {
                    "title": "Mandatory Enrolment",
                    "content": "Enrolment in the College Pension Plan shall be as set out by the College Pension Plan Rules."
                }
            }
        },
        "11": {
            "title": "EARLY RETIREMENT INCENTIVE",
            "sections": {
                "11.1": {
                    "title": "Definition",
                    "content": "For the purposes of this provision, early retirement is defined as retirement at or after age 55 and before age 64."
                },
                "11.2": {
                    "title": "Eligibility",
                    "requirements": [
                        "An employee must be at the highest achievable step of the salary scale",
                        "An employee must have a minimum of 10 years of full-time equivalent service in the BC College and Institute System"
                    ]
                },
                "11.3": {
                    "title": "Incentive Payment",
                    "payment_schedule": {
                        "age_55_to_59": "100% of Annual Salary",
                        "age_60": "80%",
                        "age_61": "60%", 
                        "age_62": "40%",
                        "age_63": "20%",
                        "age_64": "0%"
                    }
                }
            }
        },
        "12": {
            "title": "SALARIES",
            "sections": {
                "12.1": {
                    "title": "Provincial Salary Scale",
                    "subsections": {
                        "12.1.1": {
                            "title": "April 01, 2022",
                            "content": "Effective April 01, 2022, all annual salary scales shall have each step increased by $455. The resulting rates of pay will then be increased by a further 3.24%."
                        },
                        "12.1.2": {
                            "title": "April 01, 2023", 
                            "content": "Effective April 01, 2023, all salary scales shall be increased 5.5%."
                        },
                        "12.1.3": {
                            "title": "April 01, 2024",
                            "content": "Effective April 01, 2024, all salary scales shall be increased by 2%."
                        }
                    }
                },
                "12.3": {
                    "title": "Maintenance of Placement",
                    "content": "Where an employee covered by this Agreement becomes employed within two years by another institution also covered by this Agreement, initial placement shall be made at the higher of the placement formula at the hiring institution or their current or most recent salary step."
                },
                "12.5": {
                    "title": "Overload",
                    "content": "A regular employee who works an overload in a given year shall receive no less than either the pro-rata salary for the overload based on the Provincial Salary Scale or a reduction of workload in a subsequent year that is commensurate with the amount of the overload."
                }
            }
        },
        "13": {
            "title": "EFFECT OF THIS AGREEMENT",
            "sections": {
                "13.1": {
                    "content": "Where a provision of a local Collective Agreement provides a greater employee benefit than does a similar provision of this Agreement, except as noted in Clause 13.3, the local agreement provision will supersede the provision of this Agreement to the extent of the greater benefit."
                },
                "13.3": {
                    "title": "Articles Not Subject to Clause 13.1",
                    "excluded_articles": [
                        "Article 2 - Harassment",
                        "Article 3.1 - Human Resource Database", 
                        "Article 3.2.1 - 3.2.5 - Joint Administration and Dispute Resolution Committee",
                        "Article 3.3 - Expedited Arbitration",
                        "Article 4 - Prior Learning Assessment",
                        "Article 6.1.7 - Referral to JADRC",
                        "Article 6.2 - Program Transfers and Mergers",
                        "Article 6.3 - Registry of Laid Off Employees",
                        "Article 6.4 - Targeted Labour Adjustment",
                        "Article 6.5 - Contracting Out",
                        "Article 6.6 - Educational Technology/ Distributed Learning",
                        "Article 7.8 - Compassionate Care Leave",
                        "Article 7.13 - Deferred Salary Leave",
                        "Article 7.14 - Leave Respecting the Death of a Child",
                        "Article 7.15 - Leave Respecting the Disappearance of a Child",
                        "Article 7.16 - Leave for Domestic Violence",
                        "Article 7.17 - Cultural Leave for Indigenous Employees",
                        "Article 8 - Parental Leave",
                        "Article 9.1 - Joint Committee on Benefits Administration",
                        "Article 9.3 - Disability Benefits",
                        "Article 10 - Pensions",
                        "Article 12.1 and Appendix A - Provincial Salary Scale",
                        "Article 12.2 - Secondary Scale Adjustment",
                        "Article 14 - International Education",
                        "Article 16 - Common Instructor Professional Development Fund"
                    ]
                }
            }
        },
        "14": {
            "title": "INTERNATIONAL EDUCATION",
            "sections": {
                "14.1": {
                    "title": "General",
                    "provisions": [
                        "Employee participation in international education is voluntary",
                        "Subject to specific provisions, the terms and conditions of the Collective Agreement will apply",
                        "The Employer will meet and review the terms and conditions for each assignment outside Canada",
                        "The Employer will convene an annual review session for employees participating under this Article"
                    ]
                },
                "14.2": {
                    "title": "Expenses",
                    "content": "The Employer will reimburse, pursuant to employer policy, receipted expenses incurred by an Employee while on employer business. The Employer may grant a sufficient travel advance to cover anticipated expenses."
                },
                "14.3": {
                    "title": "Health and Welfare Benefits",
                    "content": "The Employer will provide current health and welfare benefits coverage for employees working under this Article. Premiums for this coverage will continue to be paid as if the employee was continuing to work for the Employer in British Columbia."
                }
            }
        },
        "15": {
            "title": "HEALTH AND SAFETY EQUIPMENT",
            "sections": {
                "15.1": {
                    "content": "The Employer agrees to supply at no cost to employees all pieces of health and safety apparel and equipment required by WorkSafeBC OH&S Regulations."
                }
            }
        },
        "16": {
            "title": "COMMON INSTRUCTOR PROFESSIONAL DEVELOPMENT FUND",
            "sections": {
                "16.1": {
                    "title": "Purpose",
                    "content": "The Common Instructor Professional Development Fund is in support of various types of professional development activities for the maintenance and development of the instructor members' professional competence and effectiveness."
                },
                "16.3": {
                    "title": "Fund",
                    "subsections": {
                        "16.3.1": "The Fund will be set at 0.7% of instructor salary for each institution.",
                        "16.3.2": "Any monies in the Fund not spent at the end of any fiscal year shall be retained by the Employer."
                    }
                }
            }
        },
        "17": {
            "title": "TERM",
            "sections": {
                "17.1": {
                    "content": "This Agreement shall be in effect from April 1, 2022 to March 31, 2025, and shall continue in force until the renewal of this Agreement."
                }
            }
        }
    },
    
    "appendices": {
        "A": {
            "title": "Provincial Salary Scale",
            "content": {
                "salary_steps": {
                    "step_1": {
                        "apr_2022_to_mar_2023": 102655,
                        "apr_2023_to_mar_2024": 109584,
                        "apr_2024_to_mar_2025": 112872
                    },
                    "step_2": {
                        "apr_2022_to_mar_2023": 96195,
                        "apr_2023_to_mar_2024": 102688,
                        "apr_2024_to_mar_2025": 105769
                    },
                    "step_3": {
                        "apr_2022_to_mar_2023": 89635,
                        "apr_2023_to_mar_2024": 95685,
                        "apr_2024_to_mar_2025": 98556
                    },
                    "step_4": {
                        "apr_2022_to_mar_2023": 85990,
                        "apr_2023_to_mar_2024": 91794,
                        "apr_2024_to_mar_2025": 94548
                    },
                    "step_5": {
                        "apr_2022_to_mar_2023": 82854,
                        "apr_2023_to_mar_2024": 88447,
                        "apr_2024_to_mar_2025": 91100
                    },
                    "step_6": {
                        "apr_2022_to_mar_2023": 79725,
                        "apr_2023_to_mar_2024": 85106,
                        "apr_2024_to_mar_2025": 87659
                    },
                    "step_7": {
                        "apr_2022_to_mar_2023": 76590,
                        "apr_2023_to_mar_2024": 81760,
                        "apr_2024_to_mar_2025": 84213
                    },
                    "step_8": {
                        "apr_2022_to_mar_2023": 73459,
                        "apr_2023_to_mar_2024": 78417,
                        "apr_2024_to_mar_2025": 80770
                    },
                    "step_9": {
                        "apr_2022_to_mar_2023": 70326,
                        "apr_2023_to_mar_2024": 75073,
                        "apr_2024_to_mar_2025": 77325
                    },
                    "step_10": {
                        "apr_2022_to_mar_2023": 67192,
                        "apr_2023_to_mar_2024": 71727,
                        "apr_2024_to_mar_2025": 73879
                    },
                    "step_11": {
                        "apr_2022_to_mar_2023": 64061,
                        "apr_2023_to_mar_2024": 68385,
                        "apr_2024_to_mar_2025": 70437
                    }
                }
            }
        },
        "B": {
            "title": "List of Investigators",
            "content": {
                "investigators": [
                    "Cheryl Otto", "Linda Sum", "Rebecca Frame", "Irene Holden", 
                    "Deborah Lovett", "Jean Greatbatch", "John Sanderson", 
                    "Marli Rusen", "Nicole Byers", "Michael Oland"
                ]
            }
        },
        "D": {
            "title": "List of Arbitrators",
            "content": {
                "arbitrators": [
                    "Chris Sullivan", "John Hall", "Komi Kandola", "Corinn Bell",
                    "Mark Brown", "Randy Noonan", "Alison Matacheskie"
                ]
            }
        },
        "F": {
            "title": "Medical Travel Referral Benefit",
            "content": {
                "benefit_summary": {
                    "deductible_amount": "None",
                    "benefit_amount": "100% of eligible expenses", 
                    "individual_maximum": "$10,000 per year",
                    "daily_limit": "$125 per day for a maximum of 50 days per calendar year"
                },
                "eligible_expenses": [
                    "Public transportation (scheduled air, rail, bus, taxi and/or ferry)",
                    "Automobile use as set out in the policy or Collective Agreement",
                    "Accommodation in a commercial facility",
                    "Reasonable and customary expenses for meals",
                    "Transportation and accommodation of an attendant where necessary"
                ]
            }
        },
        "G": {
            "title": "Dental Plan",
            "content": {
                "description": "The nine month limitation applies to 1) polishing, 2) the application of fluoride, and 3) the recall itself. The nine month limitation does not apply to scaling; any current scaling limits in dental contracts apply."
            }
        },
        "H": {
            "title": "Family Members for the Purpose of Clause 7.8 Compassionate Care Leave",
            "content": {
                "family_members_by_relationship": [
                    "Spouse", "Children", "Children's spouses", "Step-children", "Step-children-in-law",
                    "Siblings", "In-law siblings", "Parents", "Step-parents", "Parents-in-law",
                    "Grandparents", "Grandchildren", "Siblings' children", "Guardians", "Step-siblings",
                    "Parents' siblings", "Parents-in-laws' siblings", "Current or former foster-parents",
                    "Current or former foster children", "Current or former wards", "Current or former guardians"
                ],
                "family_members_by_spouse_relationship": [
                    "Spouse's parents or step-parents", "Spouse's siblings or step-siblings", "Spouse's children",
                    "Spouse's grandparents", "Spouse's grandchildren", "Spouse's parents' siblings",
                    "Spouse's siblings' children", "Spouse's current or former foster parents", "Spouse's current or former wards"
                ],
                "deemed_family_members": [
                    "Any other person in the same household who is dependent upon the employee",
                    "Any person who lives with the employee as a member of the employee's family",
                    "Whether or not related to an employee by blood, adoption, marriage or common-law partnership, an individual with a serious medical condition who considers the employee to be, or whom the employee considers to be, like a close relative"
                ]
            }
        }
    },
    
    "letters_of_understanding": {
        "1": {
            "title": "Review of Bargaining Structure and Process",
            "content": "The Employers and the Union agree to establish a Joint Review Committee to examine the potential to develop a standardized sectoral agreement(s) and review the possible standardization of the pregnancy/parental leave provisions and the grievance procedure."
        },
        "2": {
            "title": "MSP Funding Change",
            "content": "If the government, at any time in the future, reverts to an individually paid premium system for basic medical insurance, the Parties agree that the Employer will pay 100% of the premium for employees."
        },
        "3": {
            "title": "Joint Labour Management Discussion", 
            "content": "The Parties agree that it would be beneficial for the local employer and the local bargaining unit to discuss matters of mutual concern regarding contact time/instructional hours at their regular joint Union-Management meetings."
        },
        "4": {
            "title": "Public Sector General Wage Increases",
            "content": "If a public sector employer enters into a Collective Agreement with cumulative nominal general wage increases and Cost of Living Adjustments that exceed those in the 2022-2025 BCGEU Instructors Common Agreement, the total GWIs and COLAs paid out will be adjusted to be equivalent."
        },
        "5": {
            "title": "Cost of Living Adjustment", 
            "content": "Provides for Cost of Living Adjustments (COLA) to be applied to general wage increases effective April 1, 2023 (maximum 1.25%) and April 1, 2024 (maximum 1.00%) based on the annualized average of BC CPI over twelve months."
        }
    },
    
    "contact_information": {
        "bcgeu_local_712": {
            "name": "BCGEU Local 712 (Coast Mountain College)",
            "phone": "(250) 635-6511",
            "email": "local712@bcgeu.ca",
            "website": "www.bcgeu.ca"
        },
        "psea": {
            "name": "Post-Secondary Employers' Association",
            "phone": "(604) 742-0229",
            "email": "info@psea.bc.ca",
            "website": "www.psea.bc.ca"
        }
    },
    
    "citation_format": {
        "article": "Article {number}: {title}",
        "section": "Article {article_number}, Section {section_number}: {section_title}", 
        "clause": "Clause {clause_number}",
        "appendix": "Appendix {letter}: {title}",
        "lou": "Letter of Understanding {number}: {title}"
    }
}
