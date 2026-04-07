"""
server/data/contracts.py — Embedded contract clause dataset.

Each clause has:
  - text: the raw clause language
  - clause_type: ground-truth classification label
  - risk_level: "low" | "medium" | "high"
  - issues: list of legal issues present in the clause
  - improved_version: a better rewrite (for grading Task 3)
  - key_terms: terms that MUST be preserved in any rewrite
"""

from typing import List


# ──────────────────────────────────────────────────────────────
# Clause types used across all tasks
# ──────────────────────────────────────────────────────────────
CLAUSE_TYPES = [
    "indemnification",
    "limitation-of-liability",
    "termination",
    "confidentiality",
    "force-majeure",
    "intellectual-property",
    "non-compete",
    "warranty",
    "payment-terms",
    "dispute-resolution",
]


# ──────────────────────────────────────────────────────────────
# Clause datastore — 10 clauses covering the full spectrum
# ──────────────────────────────────────────────────────────────

CLAUSES = [
    # ── 0: Indemnification (Easy — straightforward) ──────────
    {
        "id": "clause_001",
        "text": (
            "The Service Provider shall indemnify and hold harmless the Client "
            "from and against any and all claims, damages, losses, costs, and "
            "expenses (including reasonable attorneys' fees) arising out of or "
            "relating to the Service Provider's breach of this Agreement or any "
            "negligent or wrongful act or omission of the Service Provider."
        ),
        "clause_type": "indemnification",
        "risk_level": "low",
        "issues": [],
        "improved_version": "",
        "key_terms": ["indemnify", "hold harmless", "claims", "damages", "breach"],
    },
    # ── 1: Limitation of Liability (Easy — classic pattern) ──
    {
        "id": "clause_002",
        "text": (
            "IN NO EVENT SHALL EITHER PARTY BE LIABLE TO THE OTHER FOR ANY "
            "INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, "
            "REGARDLESS OF THE CAUSE OF ACTION OR THE THEORY OF LIABILITY, EVEN "
            "IF SUCH PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. "
            "THE TOTAL LIABILITY OF EITHER PARTY SHALL NOT EXCEED THE AMOUNTS "
            "PAID UNDER THIS AGREEMENT IN THE TWELVE (12) MONTHS PRECEDING THE "
            "CLAIM."
        ),
        "clause_type": "limitation-of-liability",
        "risk_level": "low",
        "issues": [],
        "improved_version": "",
        "key_terms": ["liability", "indirect", "consequential", "twelve months"],
    },
    # ── 2: Termination (Medium — missing notice period) ──────
    {
        "id": "clause_003",
        "text": (
            "Either party may terminate this Agreement at any time for any reason "
            "or no reason at all, effective immediately upon written notice to "
            "the other party. Upon termination, all obligations shall cease "
            "except for those that by their nature survive termination."
        ),
        "clause_type": "termination",
        "risk_level": "medium",
        "issues": [
            "No minimum notice period specified",
            "No cure period for breach before termination",
            "No provisions for wind-down of services",
        ],
        "improved_version": (
            "Either party may terminate this Agreement: (a) for convenience upon "
            "thirty (30) days' prior written notice; or (b) for cause if the "
            "other party materially breaches this Agreement and fails to cure "
            "such breach within fifteen (15) days after receiving written notice. "
            "Upon termination, all obligations shall cease except for payment "
            "obligations, confidentiality, and those that by their nature survive."
        ),
        "key_terms": ["terminate", "written notice", "obligations", "survive"],
    },
    # ── 3: Confidentiality (Easy — standard NDA clause) ──────
    {
        "id": "clause_004",
        "text": (
            "Each party agrees to hold in confidence all Confidential Information "
            "disclosed by the other party and to use such information solely for "
            "the purposes of this Agreement. Confidential Information shall not "
            "include information that: (a) is or becomes publicly available "
            "through no fault of the receiving party; (b) was known to the "
            "receiving party prior to disclosure; or (c) is independently "
            "developed by the receiving party without use of Confidential "
            "Information."
        ),
        "clause_type": "confidentiality",
        "risk_level": "low",
        "issues": [],
        "improved_version": "",
        "key_terms": ["confidential", "disclosure", "receiving party"],
    },
    # ── 4: Force Majeure (Medium — too broad) ────────────────
    {
        "id": "clause_005",
        "text": (
            "Neither party shall be liable for any failure or delay in "
            "performance due to circumstances beyond its reasonable control, "
            "including but not limited to acts of God, war, terrorism, "
            "pandemics, government actions, labor disputes, supply chain "
            "disruptions, internet outages, market conditions, competitive "
            "pressures, management changes, or any other event that the "
            "affected party deems to be outside its control."
        ),
        "clause_type": "force-majeure",
        "risk_level": "high",
        "issues": [
            "Overly broad — 'market conditions' and 'competitive pressures' are not force majeure events",
            "'Management changes' is a controllable internal event",
            "'Any other event that the affected party deems' is subjective and unenforceable",
            "No obligation to mitigate or resume performance",
            "No termination right if force majeure extends beyond a threshold period",
        ],
        "improved_version": (
            "Neither party shall be liable for any failure or delay in "
            "performance due to circumstances beyond its reasonable control, "
            "including acts of God, war, terrorism, epidemics, government "
            "orders, or natural disasters ('Force Majeure Event'). The affected "
            "party shall: (a) promptly notify the other party; (b) use "
            "commercially reasonable efforts to mitigate the impact; and "
            "(c) resume performance as soon as reasonably practicable. If a "
            "Force Majeure Event continues for more than sixty (60) days, either "
            "party may terminate this Agreement upon written notice."
        ),
        "key_terms": ["force majeure", "reasonable control", "liable", "performance"],
    },
    # ── 5: IP Assignment (Medium — ambiguous scope) ──────────
    {
        "id": "clause_006",
        "text": (
            "All work product, inventions, and intellectual property created by "
            "the Contractor during the term of this Agreement shall be the sole "
            "and exclusive property of the Company. The Contractor hereby "
            "assigns all rights, title, and interest in such intellectual "
            "property to the Company."
        ),
        "clause_type": "intellectual-property",
        "risk_level": "medium",
        "issues": [
            "Does not distinguish between work created FOR the Company vs. personal projects",
            "No carve-out for pre-existing IP",
            "No license-back provision for Contractor's background IP used in deliverables",
        ],
        "improved_version": (
            "All work product, inventions, and intellectual property created by "
            "the Contractor in the course of performing services under this "
            "Agreement ('Work Product') shall be the sole and exclusive property "
            "of the Company. The Contractor assigns all rights in Work Product "
            "to the Company. Pre-existing intellectual property of the "
            "Contractor ('Background IP') used in deliverables is licensed to "
            "the Company on a non-exclusive, perpetual, royalty-free basis. The "
            "Contractor retains ownership of Background IP and any work created "
            "outside the scope of this Agreement."
        ),
        "key_terms": ["intellectual property", "assigns", "work product", "rights"],
    },
    # ── 6: Non-Compete (High — unreasonably broad) ──────────
    {
        "id": "clause_007",
        "text": (
            "For a period of five (5) years following termination of this "
            "Agreement, the Contractor shall not, directly or indirectly, "
            "engage in, own, manage, operate, consult for, or be employed by "
            "any business that is in any way competitive with the Company's "
            "business, anywhere in the world."
        ),
        "clause_type": "non-compete",
        "risk_level": "high",
        "issues": [
            "5-year duration is unreasonably long (courts typically enforce 1-2 years)",
            "Global geographic scope is overbroad and likely unenforceable",
            "'Any way competitive' is vague and overreaching",
            "No consideration for Contractor's ability to earn a livelihood",
        ],
        "improved_version": (
            "For a period of twelve (12) months following termination, the "
            "Contractor shall not directly provide services substantially "
            "similar to those performed under this Agreement to any direct "
            "competitor of the Company within the geographic markets where the "
            "Company actively conducts business. This restriction shall not "
            "prevent the Contractor from working in unrelated fields or for "
            "non-competing entities."
        ),
        "key_terms": ["non-compete", "termination", "competitive", "contractor"],
    },
    # ── 7: Warranty (Easy — standard) ────────────────────────
    {
        "id": "clause_008",
        "text": (
            "The Service Provider warrants that all services will be performed "
            "in a professional and workmanlike manner, consistent with generally "
            "accepted industry standards. If any services fail to meet this "
            "warranty, the Service Provider shall, at its own expense, re-perform "
            "such services. THIS WARRANTY IS IN LIEU OF ALL OTHER WARRANTIES, "
            "EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY AND "
            "FITNESS FOR A PARTICULAR PURPOSE."
        ),
        "clause_type": "warranty",
        "risk_level": "low",
        "issues": [],
        "improved_version": "",
        "key_terms": ["warranty", "workmanlike", "re-perform", "industry standards"],
    },
    # ── 8: Payment Terms (High — unfavorable to contractor) ──
    {
        "id": "clause_009",
        "text": (
            "Payment shall be due within ninety (90) days of the Company's "
            "receipt of a valid invoice, subject to the Company's satisfaction "
            "with the deliverables in its sole discretion. The Company reserves "
            "the right to withhold payment for any deliverable it deems "
            "unsatisfactory without obligation to specify the deficiency. The "
            "Contractor shall have no right to charge interest on late payments."
        ),
        "clause_type": "payment-terms",
        "risk_level": "high",
        "issues": [
            "90-day payment window is excessively long (standard is 30-45 days)",
            "'Sole discretion' gives unilateral rejection power with no check",
            "No obligation to specify deficiencies prevents Contractor from curing",
            "Prohibition on late-payment interest removes incentive for timely payment",
        ],
        "improved_version": (
            "Payment shall be due within thirty (30) days of the Company's "
            "receipt of a valid invoice. If the Company disputes a deliverable, "
            "it shall notify the Contractor in writing within ten (10) business "
            "days, specifying the deficiency. The Contractor shall have fifteen "
            "(15) days to cure. Undisputed amounts not paid within the payment "
            "period shall accrue interest at the rate of 1.5% per month."
        ),
        "key_terms": ["payment", "invoice", "deliverable", "interest"],
    },
    # ── 9: Dispute Resolution (Medium — no escalation) ──────
    {
        "id": "clause_010",
        "text": (
            "Any dispute arising under this Agreement shall be resolved "
            "exclusively through binding arbitration administered by the "
            "American Arbitration Association in accordance with its Commercial "
            "Arbitration Rules. The arbitration shall take place in New York, "
            "New York. The decision of the arbitrator shall be final and binding "
            "and may be entered as a judgment in any court of competent "
            "jurisdiction."
        ),
        "clause_type": "dispute-resolution",
        "risk_level": "medium",
        "issues": [
            "No informal negotiation step before arbitration",
            "No mediation step as intermediate resolution",
            "Single venue (New York) may be inconvenient for one party",
        ],
        "improved_version": (
            "The parties shall attempt to resolve any dispute through good-faith "
            "negotiation for thirty (30) days. If unresolved, the dispute shall "
            "be submitted to mediation under JAMS rules. If mediation fails "
            "within sixty (60) days, the dispute shall be resolved by binding "
            "arbitration under AAA Commercial Rules, held in a mutually agreed "
            "location or, failing agreement, in the respondent's jurisdiction."
        ),
        "key_terms": ["dispute", "arbitration", "binding", "jurisdiction"],
    },
]


# ──────────────────────────────────────────────────────────────
# Helper accessors
# ──────────────────────────────────────────────────────────────


def get_clause(clause_id: str) -> dict:
    """Retrieve a single clause by ID."""
    for c in CLAUSES:
        if c["id"] == clause_id:
            return c
    raise ValueError(f"Unknown clause ID: {clause_id}")


def get_clauses_by_risk(risk_level: str) -> List[dict]:
    """Filter clauses by risk level."""
    return [c for c in CLAUSES if c["risk_level"] == risk_level]


def get_clauses_by_type(clause_type: str) -> List[dict]:
    """Filter clauses by type."""
    return [c for c in CLAUSES if c["clause_type"] == clause_type]
