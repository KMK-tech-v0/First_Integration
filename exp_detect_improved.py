"""
RFO (Reason for Outage) Expression Detection System

This module provides functionality to detect and match RFO expressions against
a standardized database of fault codes and descriptions.
"""

import re
import difflib
from typing import Dict, List, Tuple, Union, Optional
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Enumeration for RFO priority levels."""
    CRITICAL_IMPACT = "Critical Impact"
    MODERATE_IMPACT = "Moderate Impact"
    MINOR_IMPACT = "Minor Impact"
    CONTEXTUAL_FACTOR = "Contextual Factor"


@dataclass
class RFOEntry:
    """Data class representing an RFO entry."""
    code: str
    root_caused: str
    priority: Priority
    normalized_root_caused: str


class RFODetector:
    """
    A class for detecting RFO expressions using exact matching, fuzzy matching,
    and substring matching techniques.
    """
    
    # Raw data string - consider moving this to a separate config file or database
    _DATA_STRING = """
Code	Root_Caused	Priority
00001	BTS, CPRI	Critical Impact
00002	BTS, RRU	Critical Impact
00003	BTS, BBU	Critical Impact
00004	BTS, CC Board	Critical Impact
00005	BTS, Power Cable	Critical Impact
00006	BTS, UMPT/UBPG	Critical Impact
00007	BTS, BPK	Critical Impact
00008	BTS, Back Plane	Critical Impact
00009	BTS, Controller Card	Critical Impact
00010	BTS, UBBP	Critical Impact
00011	BTS, Power Breaker	Critical Impact
00012	BTS, AAU	Critical Impact
00013	BTS, Fan	Critical Impact
00014	BTS, SFP Module	Critical Impact
00015	BTS, Jumper Cable	Critical Impact
00016	BTS, FS	Critical Impact
00017	BTS, BPN	Critical Impact
00018	BTS, PM card	Critical Impact
00019	BTS, CC card	Critical Impact
00020	BTS, Power connector	Critical Impact
00021	BTS, Power Socket	Critical Impact
00022	BTS, Power Connector (duplicate entry)	Critical Impact
00023	BTS, CR0	Critical Impact
00024	Catastrophic	Contextual Factor
00025	DG, Engine Fault	Critical Impact
00026	DG, Alternator fault	Critical Impact
00027	DG, GMU/Display board fault	Moderate Impact
00028	DG, Fueling pump fault	Critical Impact
00029	DG, Fueling sensor fault	Critical Impact
00030	DG, Fuel Pipe	Critical Impact
00031	DG, Radiator	Critical Impact
00032	DG, Controller	Critical Impact
00033	DG, Starter Battery	Critical Impact
00034	DG, Hand Pump	Minor Impact
00035	DG, Low Oil Pressure	Critical Impact
00036	DG, Fuel Choke	Minor Impact
00037	DG, Coolant	Minor Impact
00038	DG, Starting motor fault 	Minor Impact
00039	DG, Relay damaged /burnt	Minor Impact
00040	DG, Solenoid stuck 	Moderate Impact
00041	DG, AVR fault	Moderate Impact
00042	DG, MCB fault	Moderate Impact
00043	DG, air senor fault	Minor Impact
00044	DG, Engine Oil	Critical Impact
00045	DG, oil sensor fault	Critical Impact
00046	DG, Exhaust Pipe	Moderate Impact
00047	DG, water sensor fault	Minor Impact
00048	DG, auxiliary oil level sensor fault	Minor Impact
00049	DG, fan broken	Moderate Impact
00050	DG, fan belt broken	Moderate Impact
00051	DG, govenor fault	Moderate Impact
00052	DG, oil filter dirty	Minor Impact
00053	DG, fuel filter & water separator dirty	Moderate Impact
00054	DG, Start stop cable	Minor Impact
00055	DG, water hose damaged	Moderate Impact
00056	DG, thermostat fault	Moderate Impact
00057	DG, cycling oil pump fault	Minor Impact
00058	DG, Overload	Critical Impact
00059	DG, gasket	Critical Impact
00060	DG, Timer Delay	Moderate Impact
00061	DG, Manual	Minor Impact
00062	DG, Water Pipe	Minor Impact
00063	DG, Air filter	Moderate Impact
00064	DG, Plunger Fault	Minor Impact
00065	DG, Pressure pump	Moderate Impact
00066	DG, Fuel Injector	Critical Impact
00067	DG, Air lock	Critical Impact
00068	DG, Water Cup	Minor Impact
00069	DG, Start relay	Minor Impact
00070	DG, Water Tank	Moderate Impact
00071	DG, Engine Head	Critical Impact
00072	DG, fan belt loose	Minor Impact
00073	DG, Piston Fault	Critical Impact
00074	DG, Timer Fail	Moderate Impact
00075	DG, Fuel Injection pump	Moderate Impact
00076	DG Auto Pump	Moderate Impact
00077	DG, Mounting	Moderate Impact
00078	DG, water leakage	Moderate Impact
00079	DG, Auto Pump	Moderate Impact
00080	DG, Negative phase	Moderate Impact
00081	DG, fuel pump fault	Moderate Impact
00082	DG, solenoid	Moderate Impact
00083	DG, Air sensor fault	Moderate Impact
00084	DG, Under speed	Moderate Impact
00085	DG, Starter Motor	Moderate Impact
00086	DG, Over voltage	Moderate Impact
00087	DG, Magnetic conductor	Moderate Impact
00088	DG, Under voltage	Moderate Impact
00089	DG, Under Frequency	Moderate Impact
00090	DG, Nozzle Faulty	Moderate Impact
00091	DG, Battery Cable Loose	Moderate Impact
00092	DG, Engine Oil Pipe	Moderate Impact
00093	DG, Water Pump	Moderate Impact
00094	Permanent DG issue	Moderate Impact
00095	Engine oil/Cooling water	Moderate Impact
00096	RCUB card	Critical Impact
00097	Low Fuel Quality	Moderate Impact
00098	Fuel Theft	Moderate Impact
00099	Construction	Contextual Factor
00100	Force majeure	Contextual Factor
00101	Partial natural core damaged	Moderate Impact
00102	Animal bite	Critical Impact
00103	Intentional cut	Critical Impact
0104	Car accident	Critical Impact
00105	Patch cord cut	Moderate Impact
00106	DWDM Fiber	Critical Impact
00107	MFOCN Fiber	Critical Impact
00108	Fire	Contextual Factor
00109	Flood	Contextual Factor
00110	DG, Fuel Shortage	Critical Impact
00111	DG, Fuel/water mixed	Moderate Impact
00112	EPC Department Maintenance 	Moderate Impact
00113	EPC Outage > 4 Hrs.	Moderate Impact
00114	EPC Outage > 6 Hrs.	Moderate Impact
00115	Movement Restriction	Contextual Factor
00116	MW Realignment	Moderate Impact
00117	MW Fading due to bad weather	Moderate Impact
00118	MW bandwidth congestion	Moderate Impact
00119	DG Restriction in night time	Contextual Factor
00120	DG Restriction in day time	Contextual Factor
00121	Meter bill payment expired	Contextual Factor
00122	Contact expired	Contextual Factor
00123	Other payment issue	Contextual Factor
00124	Night Time Access	Contextual Factor
00125	Owner restrict	Contextual Factor
00126	Permission Issue	Contextual Factor
00127	DG Manual	Moderate Impact
00128	RCD 1 Breaker Hang	Critical Impact
00129	Meter box burn	Critical Impact
00130	Power cable damaged	Critical Impact
00131	Battery Cells Fault	Critical Impact
00132	Rectifier hardware issue	Critical Impact
00133	ATS Relay	Critical Impact
00134	ATS Breaker	Critical Impact
00135	Smoke sensor fault	Critical Impact
00136	Voltage Fluctuation	Critical Impact
00137	Cable theft	Critical Impact
00138	PDU Hang	Moderate Impact
00139	Cabinet Breaker	Moderate Impact
00140	ACDU/DCDU faulty	Moderate Impact
00141	ECC500 faulty	Moderate Impact
00142	Hum-Teem sensor fault	Moderate Impact
00143	Door switch fault	Moderate Impact
00144	Battery temperature sensor fault	Moderate Impact
00145	DC air conditioner fault	Moderate Impact
00146	Heater exchanger fault	Moderate Impact
00147	BLVD fault	Moderate Impact
00148	Power cable loose	Minor Impact
00149	Cabinet Battery	Minor Impact
00150	Cabinet controller	Minor Impact
00151	Solar plane damaged	Minor Impact
00152	Night Time Access	Minor Impact
00153	Owner not Available	Minor Impact
00154	Permission Issue	Minor Impact
00155	Meter bill payment expired	Minor Impact
00156	Contact expired	Minor Impact
00157	Other payment issue	Minor Impact
00158	Cable wrong connection	Minor Impact
00159	Cable loose connection	Minor Impact
00160	Cable damage	Minor Impact
00161	CSU	Minor Impact
00162	PSU fault	Minor Impact
00163	SSU fault	Minor Impact
00164	EM Hung	Minor Impact
00165	ATS Hung	Minor Impact
00166	MUS01A fault	Minor Impact
00167	MUE03A fault	Minor Impact
00168	MUE05A fault	Minor Impact
00169	SMR Module	Minor Impact
00170	PU Module	Minor Impact
00171	Power Socket	Minor Impact
00172	Pure Solar	Moderate Impact
00173	Tree shadow issue	Moderate Impact
00174	Power Cable Stolen	Contextual Factor
00175	Battery Stolen	Contextual Factor
00176	Cable Stolen	Contextual Factor
00177	TX, E1 link error	Critical Impact
00178	TX, IDU (Indoor Unit)	Critical Impact
00179	TX, ODU (Outdoor Unit)	Critical Impact
00180	TX, RTN (Return Transmission)	Critical Impact
00181	TX, Power Cable	Critical Impact
00182	TX, LAN Switch	Critical Impact
00183	TX, VSAT Modem	Critical Impact
00184	TX, IF Cable	Moderate Impact
00185	TX, ATN (Access Transport Network)	Moderate Impact
00186	TX, PTN (Packet Transport Network)	Moderate Impact
00187	TX, Patch Cord	Moderate Impact
00188	TX, SFP Module	Moderate Impact
00189	TX, LAN Cable	Moderate Impact
00190	TX, Pig tail	Moderate Impact
00191	TX, Modem card	Moderate Impact
00192	TX, IF connector	Moderate Impact
00193	TX, Power injector	Moderate Impact
00194	TX, ATMU (Alarm Transmission Monitoring Unit)	Minor Impact
00195	TX, RMUH (Remote Monitoring Unit)	Minor Impact
00196	TX, RRN (reset)	Minor Impact
00197	Unsafe Zone	Contextual Factor
00198	Vandalism	Contextual Factor
00199	ETA	Contextual Factor
00200	Power Sharing	Moderate Impact
00201	Hub Site Impact	Critical Impact
00202	DCDB cable	Critical Impact
00203	BTS, RCUC card	Critical Impact
00204	EPC outage	Moderate Impact
00205	BTS, hardware	Moderate Impact
00206	TX, hardware	Moderate Impact
00207	Fiber cut access	Critical Impact
00208	Fiber cut BB	Critical Impact
00209	Vsat router	Critical Impact
00210	Team will check at morning	Contextual Factor
00211	DG Hardware issue	Contextual Factor
00212	TX , Transmission	Contextual Factor
00213	Redcing fuel consumption due to higher pice	Critical Impact
00214	DG, backup battery	Moderate Impact
00215	Earthquake	Critical Impact
00216	Site access issue	Critical Impact
"""

    def __init__(self):
        """Initialize the RFO detector with parsed data."""
        self.rfo_entries: List[RFOEntry] = self._parse_rfo_data()
        
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text for comparison by:
        - Converting to lowercase
        - Removing content within parentheses
        - Removing non-alphanumeric characters (except spaces)
        - Replacing multiple spaces with single space
        - Stripping leading/trailing whitespace
        
        Args:
            text: Input text to normalize
            
        Returns:
            Normalized text string
        """
        if not text:
            return ""
            
        text = text.lower()
        text = re.sub(r'\s*\([^)]*\)\s*', '', text)  # Remove parentheses content
        text = re.sub(r'[^a-z0-9\s]', '', text)     # Keep only alphanumeric and spaces
        text = re.sub(r'\s+', ' ', text).strip()    # Normalize whitespace
        return text

    def _parse_rfo_data(self) -> List[RFOEntry]:
        """
        Parse the multiline string data into RFOEntry objects.
        
        Returns:
            List of RFOEntry objects
        """
        lines = self._DATA_STRING.strip().split('\n')
        if not lines:
            return []
            
        # Skip header line
        rfo_entries = []
        for line in lines[1:]:
            if not line.strip():
                continue
                
            # Split by tab first, then fallback to multiple spaces
            parts = line.split('\t')
            if len(parts) < 3:
                # Fallback to splitting by multiple spaces
                parts = [p.strip() for p in re.split(r'\s{2,}', line.strip())]
            else:
                parts = [p.strip() for p in parts]
            
            if len(parts) >= 3:  # Ensure we have at least code, root_caused, priority
                code = parts[0]
                root_caused = parts[1]
                priority_str = parts[2]
                
                # Convert priority string to enum
                try:
                    priority = Priority(priority_str)
                except ValueError:
                    # Default to moderate impact if priority not recognized
                    priority = Priority.MODERATE_IMPACT
                
                normalized_root_caused = self._normalize_text(root_caused)
                
                rfo_entries.append(RFOEntry(
                    code=code,
                    root_caused=root_caused,
                    priority=priority,
                    normalized_root_caused=normalized_root_caused
                ))
        
        return rfo_entries

    def detect_rfo_expression(self, expression_word: str, fuzzy_threshold: float = 0.8) -> Union[Tuple[str, str], str]:
        """
        Detect if an expression word matches any standard RFO using multiple matching strategies.
        
        Matching strategies (in order of priority):
        1. Exact match on normalized text
        2. Fuzzy matching using sequence similarity
        3. Substring matching (bidirectional)
        
        Args:
            expression_word: The input string to check against RFOs
            fuzzy_threshold: Minimum similarity ratio (0.0 to 1.0) for fuzzy matching
            
        Returns:
            Tuple of (code, root_caused) if match found, otherwise error message string
        """
        if not expression_word or not expression_word.strip():
            return "Empty expression provided"
            
        if not 0.0 <= fuzzy_threshold <= 1.0:
            raise ValueError("fuzzy_threshold must be between 0.0 and 1.0")
        
        normalized_expression = self._normalize_text(expression_word)
        
        if not normalized_expression:
            return "Expression contains no valid characters"
        
        # Strategy 1: Exact match (highest priority)
        exact_match = self._find_exact_match(normalized_expression)
        if exact_match:
            return exact_match
        
        # Strategy 2: Fuzzy matching
        fuzzy_match = self._find_fuzzy_match(normalized_expression, fuzzy_threshold)
        if fuzzy_match:
            return fuzzy_match
        
        # Strategy 3: Substring matching
        substring_match = self._find_substring_match(normalized_expression)
        if substring_match:
            return substring_match
        
        return "expression need to be upgrade"

    def _find_exact_match(self, normalized_expression: str) -> Optional[Tuple[str, str]]:
        """Find exact match for normalized expression."""
        for rfo in self.rfo_entries:
            if normalized_expression == rfo.normalized_root_caused:
                return (rfo.code, rfo.root_caused)
        return None

    def _find_fuzzy_match(self, normalized_expression: str, threshold: float) -> Optional[Tuple[str, str]]:
        """Find best fuzzy match above threshold."""
        best_match = None
        highest_similarity = 0.0
        
        for rfo in self.rfo_entries:
            similarity = difflib.SequenceMatcher(
                None, 
                normalized_expression, 
                rfo.normalized_root_caused
            ).ratio()
            
            if similarity >= threshold and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = (rfo.code, rfo.root_caused)
        
        return best_match

    def _find_substring_match(self, normalized_expression: str) -> Optional[Tuple[str, str]]:
        """Find substring match (bidirectional)."""
        for rfo in self.rfo_entries:
            # Check if expression is contained in RFO
            if normalized_expression in rfo.normalized_root_caused:
                return (rfo.code, rfo.root_caused)
            
            # Check if RFO is contained in expression
            if rfo.normalized_root_caused in normalized_expression:
                return (rfo.code, rfo.root_caused)
        
        return None

    def get_rfo_by_code(self, code: str) -> Optional[RFOEntry]:
        """
        Get RFO entry by code.
        
        Args:
            code: RFO code to search for
            
        Returns:
            RFOEntry if found, None otherwise
        """
        for rfo in self.rfo_entries:
            if rfo.code == code:
                return rfo
        return None

    def get_rfos_by_priority(self, priority: Priority) -> List[RFOEntry]:
        """
        Get all RFO entries with specified priority.
        
        Args:
            priority: Priority level to filter by
            
        Returns:
            List of RFOEntry objects with matching priority
        """
        return [rfo for rfo in self.rfo_entries if rfo.priority == priority]

    def search_rfos(self, search_term: str) -> List[RFOEntry]:
        """
        Search RFO entries by root cause description.
        
        Args:
            search_term: Term to search for in root cause descriptions
            
        Returns:
            List of matching RFOEntry objects
        """
        normalized_search = self._normalize_text(search_term)
        if not normalized_search:
            return []
        
        matches = []
        for rfo in self.rfo_entries:
            if normalized_search in rfo.normalized_root_caused:
                matches.append(rfo)
        
        return matches


def run_comprehensive_tests():
    """Run comprehensive tests for the RFO detector."""
    detector = RFODetector()
    
    test_cases = [
        # Exact matches
        ('BTS, CPRI', 'Should match exactly'),
        ('  bts, cpri  ', 'Should handle whitespace'),
        ('BTS ,  CPRI', 'Should handle irregular spacing'),
        
        # Fuzzy matches
        ('dbd modul issue', 'Should fuzzy match DCDB cable'),
        ('rectifier hardwar issue', 'Should handle typo in hardware'),
        ('fueling pump falt', 'Should handle typo in fault'),
        ('battry cells fault', 'Should handle typo in battery'),
        
        # Substring matches
        ('DG Engine Fault', 'Should match DG, Engine Fault'),
        ('Engine Fault', 'Should match via substring'),
        ('fiber cut', 'Should match fiber cut entries'),
        ('cable stolen', 'Should match Cable Stolen'),
        
        # Edge cases
        ('', 'Empty string'),
        ('   ', 'Whitespace only'),
        ('Unknown Issue', 'No match expected'),
        ('xyz123', 'Random string'),
    ]
    
    print("=== RFO Detection Test Results ===\n")
    
    for expression, description in test_cases:
        result = detector.detect_rfo_expression(expression)
        print(f"Test: '{expression}' ({description})")
        print(f"Result: {result}")
        print("-" * 50)


# Legacy function for backward compatibility
def detect_rfo_expression(expression_word: str, fuzzy_threshold: float = 0.8) -> Union[Tuple[str, str], str]:
    """
    Legacy function for backward compatibility.
    
    Args:
        expression_word: The input string to check against RFOs
        fuzzy_threshold: Minimum similarity ratio for fuzzy matching
        
    Returns:
        Tuple of (code, root_caused) if match found, otherwise error message string
    """
    detector = RFODetector()
    return detector.detect_rfo_expression(expression_word, fuzzy_threshold)


if __name__ == "__main__":
    # Run tests when script is executed directly
    run_comprehensive_tests()
    
    # Example usage
    print("\n=== Example Usage ===")
    detector = RFODetector()
    
    # Search for critical impact RFOs
    critical_rfos = detector.get_rfos_by_priority(Priority.CRITICAL_IMPACT)
    print(f"Found {len(critical_rfos)} critical impact RFOs")
    
    # Search for power-related issues
    power_issues = detector.search_rfos("power")
    print(f"Found {len(power_issues)} power-related RFOs")
    
    # Get specific RFO by code
    rfo = detector.get_rfo_by_code("00001")
    if rfo:
        print(f"RFO 00001: {rfo.root_caused} ({rfo.priority.value})")
