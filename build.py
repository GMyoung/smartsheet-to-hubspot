"""Build data.js for the site: the two fake Smartsheet logs, the dictionary rows and where each one is on a HubSpot screenshot.

    python -I build.py

The dictionary text comes from the HubSpot project (scripts/smartsheet_dictionary.py); sheets.json holds the fake rows
(no real patient). Rectangles are x, y, width, height in pixels on the 1568 x 726 screenshots in img/.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, r'E:\CodeX\hubspot-ict-cm\scripts')
import smartsheet_dictionary as d  # noqa: E402

SCREENS = [
    ('new-patient', 'New ICT Patient page', 'Create the patient'),
    ('overview-1', 'Patient page: Overview tab', 'Open the patient'),
    ('overview-3', 'Overview tab: Medical Follow-up, and the left card', 'Open the patient'),
    ('demographics-1', 'Patient Demographics tab: Patient', 'Patient Demographics'),
    ('demographics-2', 'Patient Demographics tab: Contact and Address', 'Patient Demographics'),
    ('demographics-3', 'Patient Demographics tab: Emergency Contacts, Parent / Guardian', 'Patient Demographics'),
    ('ed-visit', 'Hospital EMR tab: ED Visit', 'Hospital EMR'),
    ('ed-notes', 'Hospital EMR tab: ED Visit Notes', 'Hospital EMR'),
    ('tracker-1', 'Hospital EMR tab: Hospital EMR Tracker', 'Hospital EMR'),
    ('tracker-2', 'Hospital EMR Tracker: lien, records, review, settlement', 'Hospital EMR'),
    ('tracker-3', 'Hospital EMR Tracker: closing the account', 'Hospital EMR'),
    ('log-call', 'Log a Call', 'Calls'),
    ('insurance-top', 'Insurance and Verification tab', 'Insurance'),
    ('insurance-form', 'Insurance card: New Insurance', 'Insurance'),
    ('insurance-policy', 'Insurance card: a saved policy', 'Insurance'),
    ('insurance-verify', 'Insurance card: Verify a policy', 'Insurance'),
    ('insurance-notpl', 'Insurance tab: Health Insurance, No TPL / No Case Confirmation', 'Insurance'),
    ('attorney-top', 'Patient Attorney tab', 'Attorney'),
    ('attorney-form', 'Attorneys card: New Attorney', 'Attorney'),
    ('attorney-verify', 'Attorneys card: Add New Verification', 'Attorney'),
    ('patients-list', 'ICT Patients list', 'Open the patient'),
    ('tabs-more', 'Patient page: the More tabs', 'Open the patient'),
    ('activities-menu', 'Patient page: Add activities', 'Calls'),
]

CASE_TYPE = ('insurance-top', [573, 199, 270, 36], 'Case Type')
ADD_INSURANCE = ('insurance-top', [634, 494, 116, 29], '+ Add Insurance')
STAGE = ('overview-1', [233, 377, 150, 36], 'Stage')
NO_TPL = ('insurance-notpl', [555, 373, 611, 198], 'No TPL / No Case Confirmation')
STATUS = ('attorney-top', [571, 336, 190, 36], 'Attorney Status')
CARE = ('overview-3', [555, 257, 611, 85], 'Liens and Care: the Care Coordination record')
APPOINTMENT = ('overview-3', [581, 563, 575, 140], 'Initial Appointment')
INJURY = ('ed-visit', [571, 524, 590, 66], 'Incident Type, Injured Body Parts, Other Injury Notes')
CLOSE = ('tracker-3', [555, 362, 611, 248], 'No TPL Discovered: Close the Account')
OUTCOME = ('log-call', [1008, 352, 75, 40], 'Call outcome')

TARGETS = {
    'Date / Intake DATE': [('overview-3', [233, 380, 200, 36], 'ICT Intake Date'), ('ed-visit', [772, 607, 190, 36], 'ICT Intake Date')],
    'LAST NAME (GUARDIAN)': [('new-patient', [532, 187, 170, 53], 'Last Name'), ('demographics-1', [974, 304, 180, 36], 'Last Name'),
                             ('demographics-3', [555, 449, 611, 231], 'Parent / Guardian (for a patient under 18)')],
    'FIRST NAME': [('new-patient', [352, 187, 170, 53], 'First Name'), ('demographics-1', [571, 304, 190, 36], 'First Name')],
    'DOB': [('new-patient', [352, 328, 370, 53], 'Date of Birth'), ('demographics-1', [571, 417, 190, 36], 'Date of Birth')],
    'Language / LANGUAGE': [('new-patient', [352, 398, 97, 53], 'Patient Language'), ('demographics-1', [974, 417, 180, 36], 'Patient Language'),
                            ('demographics-1', [571, 474, 190, 36], 'Interpreter Needed')],
    'PHONE': [('new-patient', [352, 257, 170, 53], 'Phone Number'), ('demographics-2', [573, 200, 270, 93], 'Phone Number, Secondary Phone Number')],
    'Additional Contact Info': [('demographics-3', [555, 227, 611, 201], 'Emergency Contacts'), ('demographics-3', [555, 449, 611, 231], 'Parent / Guardian')],
    'ADDRESS': [('demographics-2', [866, 145, 298, 410], 'Address')],
    'EMAIL': [('demographics-2', [573, 314, 270, 36], 'Email')],
    'MRN': [('new-patient', [352, 468, 170, 53], 'MRN'), ('ed-visit', [571, 277, 190, 36], 'MRN')],
    'Account Number': [('new-patient', [532, 468, 170, 53], 'Hospital Account Number'), ('ed-visit', [772, 277, 190, 36], 'Hospital Account Number')],
    'HPH ER': [('new-patient', [459, 398, 170, 53], 'Hospital Facility'), ('ed-visit', [571, 467, 190, 36], 'Hospital Facility')],
    'Patient Engagement Specialist': [('overview-1', [573, 465, 270, 36], 'Owner')],
    'Date Of Injury (DOI)': [('ed-visit', [974, 467, 180, 36], 'Date of Injury'), ('insurance-top', [573, 255, 270, 36], 'Date of Injury')],
    '(new) Date of Service (DOS)': [('new-patient', [352, 539, 370, 53], 'Date of Service (DOS)'), ('ed-visit', [772, 467, 190, 36], 'Date of Service (DOS)')],
    'BIBA': [('ed-visit', [571, 607, 190, 36], 'BIBA')],
    'Chief Complaint / CHIEF COMPLAINT': [INJURY],
    'Provider Notes': [('ed-notes', [555, 435, 611, 245], 'ED Visit Notes')],
    'DETAIL/ADMISSION STATUS': [('ed-notes', [555, 435, 611, 245], 'What the hospital wrote: ED Visit Notes'),
                                ('log-call', [927, 430, 492, 45], 'What the patient told us: the notes of the call'), CASE_TYPE],
    'ED visit charges ($)': [('ed-visit', [974, 607, 180, 36], 'ER Bill Amount')],
    'INTAKE/TIME TO CALL': [('log-call', [927, 580, 390, 22], 'A follow-up task: its time is the Callback Time')],
    'INTAKE TIMESTAMP': [('overview-1', [1257, 377, 243, 108], 'Created: recorded by the system')],
    'LINK TO PATIENT FILES': [('overview-1', [555, 358, 611, 62], 'All Files'), ('insurance-top', [573, 312, 270, 110], 'Police / Crash Report, Case Files')],
    'Came Back to ER': [('new-patient', [352, 539, 370, 53], 'A new patient with the new DOS')],
    'Lead Owner': [('overview-1', [573, 465, 270, 36], 'Owner')],
    'Calling Team Agent': [('overview-1', [866, 443, 298, 135], 'Last Contact: who called')],
    'CONTACT DATE': [('overview-1', [866, 443, 298, 135], 'Last Contact: when, and how many attempts'), ('log-call', [1228, 352, 170, 55], 'Activity date')],
    'Case Management DETAILS': [('log-call', [927, 430, 492, 45], 'The notes of the call'), ('overview-1', [1217, 93, 306, 415], 'Notes and Calls')],
    'LTM/LVM': [OUTCOME],
    'No Answer/ No contact': [OUTCOME],
    'NO CALL/Pt REFUSED': [STAGE],
    'PI': [CASE_TYPE], 'WC': [CASE_TYPE], 'Maybe TPL': [CASE_TYPE], 'At fault Drivers': [CASE_TYPE],
    'NO TPL/NO CASE': [CASE_TYPE, NO_TPL],
    'Not finalised/Unclear TPL Status': [CASE_TYPE],
    'Referral Case': [STATUS],
    'Lost Case': [STAGE],
    'Private health insurance': [('insurance-notpl', [555, 262, 611, 70], 'Health Insurance'), ADD_INSURANCE],
    'Commercial insurance': [ADD_INSURANCE],
    'Nursing Home': [INJURY],
    'School/Sports injury': [INJURY],
    'Union WC': [CASE_TYPE, ADD_INSURANCE],
    'Federal WC': [CASE_TYPE, ADD_INSURANCE],
    'Insurance / Responsible Payer': [('insurance-form', [555, 145, 611, 581], 'New Insurance: one box per fact'),
                                      ('insurance-policy', [555, 463, 611, 263], 'The saved policy'),
                                      ('insurance-top', [573, 312, 270, 48], 'Police / Crash Report')],
    'Health insurance carrier': [('insurance-notpl', [555, 262, 611, 70], 'Health Insurance')],
    'MedPay/ UIM': [ADD_INSURANCE],
    'TPL Insurance confirmed': [('insurance-verify', [573, 397, 571, 300], 'Verify'), ('insurance-policy', [632, 512, 58, 18], 'Verified')],
    'Insurance Info Last Update Timestamp': [('insurance-verify', [574, 242, 350, 36], 'Added On, Last Verified On')],
    'Insurance Team Agent': [('insurance-verify', [573, 355, 216, 20], 'Verification History: who verified')],
    'Insurance added to EZDocs': [('tracker-1', [574, 457, 270, 36], 'TPL/WC Insurance Added to Hospital Date')],
    'AgreeD to speak to IN network Atty': [STATUS],
    'Referral Timestamp / ATTY Referral Date': [('attorney-top', [772, 336, 190, 36], 'Referred to Attorney Date')],
    "Attorney's Detail": [('attorney-form', [573, 137, 571, 148], 'Attorney Name, Law Firm'), ('attorney-top', [555, 583, 611, 130], 'Current Patient Attorney')],
    'Attorney Contact Details': [('attorney-form', [573, 312, 571, 256], 'Phone, Fax, Email, Address')],
    "Agreement sent/ PT's not sent back yet": [('attorney-top', [772, 336, 382, 36], 'Referred date filled, Signed date still empty')],
    'Signed with Atty; Signing Date with IN-N Atty': [('attorney-top', [974, 336, 180, 36], 'Attorney Signed Date')],
    'Attorney Declined Case': [('attorney-top', [571, 393, 190, 36], 'Attorney Rejected Date')],
    'Patient has own Atty': [STATUS],
    'Own Attorney; Own Law-Firm; Own Atty/Law-Firm Detail': [('attorney-form', [573, 137, 571, 431], 'New Attorney')],
    'Signed with OUT-N Atty': [('attorney-verify', [572, 397, 572, 300], 'Add New Verification'), ('attorney-top', [573, 632, 133, 19], 'Representing (Verified)')],
    'Needs Appt': [('overview-3', [581, 425, 190, 36], 'Medical Follow-up')],
    'Appt Scheduled': [APPOINTMENT],
    'Appt Location': [('overview-3', [581, 511, 572, 36], 'Medical Follow-up Destination, Provider Name and Location')],
    'Medical Appt Details': [APPOINTMENT, ('overview-3', [776, 425, 190, 36], 'Medical Follow-up Note')],
    'Medical Follow-up Details': [CARE],
    'Scheduled Extra Appointment; Details Of EA': [CARE],
    'Referred Back To HPH / NM': [('overview-3', [581, 511, 280, 36], 'Medical Follow-up Destination')],
    'Accepted By HPH / NWM': [APPOINTMENT],
    'Added to Nimbly': [('overview-3', [233, 567, 260, 55], 'Nimbly Patient Link')],
    'Billing Indicator Added to HPH / EPIC': [('tracker-1', [556, 279, 48, 20], 'H1 BI'), ('overview-3', [233, 520, 200, 36], 'BI Added Date')],
    'Billing Added To EPIC': [('tracker-1', [558, 353, 297, 274], 'H2 Coverage Added to Hospital EMR')],
    'No TPL Coverage': [NO_TPL],
    'No Discovery - Closed after 30 days': [CLOSE, ('tracker-1', [554, 238, 170, 20], 'The hospital deadline')],
    'Account Closed': [CLOSE],
    'MR & BILLING SENT; MR & BILLING DETAILS': [('tracker-2', [866, 231, 297, 190], 'H5 Medical Records and Bill (MR&B)')],
    '(new) Liens, hospital bills and payments': [('tracker-2', [558, 231, 297, 190], 'H4 Lien: made on the Lien and Collection tab')],
}


# ---- The walkthrough (user, 2026-11-16: "walk through 是从点进那个病人开始"): the ICT Patients list, the patient, the tab,
# the click that opens a form, then the field. A field typed when the patient is created comes last, on the New ICT Patient page.
LIST_STEP = ('patients-list', [276, 289, 142, 26], "Open ICT Patients in the left menu and click the patient's name.")
WIDE = ' (On a wide screen the tab is in the row itself.)'
TAB_STEP = {
    'Overview': ('overview-1', [535, 93, 102, 38], 'The patient page opens. Click the Overview tab if another tab is showing.'),
    'Hospital EMR': ('overview-1', [637, 93, 120, 38], 'On the patient page, click the Hospital EMR tab.'),
    'Patient Demographics': ('overview-1', [757, 93, 168, 38], 'On the patient page, click the Patient Demographics tab.'),
    'Insurance and Verification': ('tabs-more', [945, 152, 160, 24], 'On the patient page, click More, then Insurance and Verification.' + WIDE),
    'Patient Attorney': ('tabs-more', [945, 185, 160, 24], 'On the patient page, click More, then Patient Attorney.' + WIDE),
    'Log a Call': ('activities-menu', [1298, 294, 190, 24],
                   'On the patient page, click Add activities, then Log a call. (The Call button under the patient name does the same.)'),
}
TAB_OF = {'overview': 'Overview', 'demographics': 'Patient Demographics', 'ed': 'Hospital EMR', 'tracker': 'Hospital EMR',
          'insurance': 'Insurance and Verification', 'attorney': 'Patient Attorney', 'log': 'Log a Call'}
BEFORE = {
    'insurance-form': ('insurance-top', [634, 494, 116, 29], 'Click + Add Insurance and pick the Coverage Type.'),
    'insurance-verify': ('insurance-notpl', [573, 180, 61, 27], 'On the policy, click Verify.'),
    'attorney-form': ('attorney-top', [634, 239, 111, 27], 'Click + Add Attorney.'),
}


def walk(targets):
    page = [t for t in targets if t[0] != 'new-patient']
    steps, tab = [], None
    if page:
        steps.append(LIST_STEP + ('open',))
    for screen, rect, label in page:
        left = rect[0] < 520
        name = TAB_OF[screen.split('-')[0]]
        if not left and name != tab:
            steps.append(TAB_STEP[name] + ('tab',))
            tab = name
        if screen in BEFORE and BEFORE[screen] + ('click',) not in steps:
            steps.append(BEFORE[screen] + ('click',))
        steps.append((screen, rect, f'Here it is: {label}.' + (' It is on the left card, whichever tab is open.' if left else ''), 'field'))
    for screen, rect, label in targets:
        if screen == 'new-patient':
            steps.append((screen, rect, (f'For a new patient you type it first, on the New ICT Patient page: {label}.' if page
                                         else f'On the New ICT Patient page: {label}.'), 'create'))
    return [{'screen': a, 'rect': b, 'text': c, 'kind': k} for a, b, c, k in steps]


# Row colours as staff used them (the sheet's Color Keys column); the first rule that fits.
ROW_RULES = [('red', ['NO CALL/Pt REFUSED', 'NO TPL/NO CASE']), ('blue', ["Agreement sent/ PT's not sent back yet"]),
             ('green', ['AgreeD to speak to IN network Atty', 'Signed with Atty']), ('white', ['Patient has own Atty']),
             ('grey', ['LTM/LVM', 'No Answer/ No contact']), ('yellow', ['Appt Scheduled', 'Apoointment Scheduled']), ('pink', ['Needs Appt', 'NEEDS APPOINTMENT'])]


def row_colors(sheet):
    at = {h: i for i, h in enumerate(sheet['header'])}
    return [next((color for color, heads in ROW_RULES if any(h in at and row[at[h]] is True for h in heads)), 'white') for row in sheet['rows']]


def shift_dates(text, days=160):
    """The first fake patient's 2026 dates moved to the month of the HubSpot screenshots (the birth date stays)."""
    def moved(m, sep, order):
        a, b, y = m.group(1), m.group(2), m.group(3)
        if y not in ('26', '2026'):
            return m.group(0)
        day = datetime.date(2026, int(a), int(b)) + datetime.timedelta(days=days)
        pad = len(a) == 2
        return sep.join([f'{day.month:02d}' if pad else str(day.month), f'{day.day:02d}' if pad else str(day.day), str(day.year)[-len(y):]])
    text = re.sub(r'\b(\d{1,2})/(\d{1,2})/(\d{4}|\d{2})\b', lambda m: moved(m, '/', 0), text)
    return re.sub(r'\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b', lambda m: moved(m, '.', 0), text)


def letters(n):
    out = []
    for i in range(n):
        s, k = '', i
        while True:
            s = chr(65 + k % 26) + s
            k = k // 26 - 1
            if k < 0:
                break
        out.append(s)
    return out


def main():
    sheets = json.load(open(os.path.join(HERE, 'sheets.json'), encoding='utf-8'))
    sheets['hph']['rows'][0] = [shift_dates(v) if isinstance(v, str) else v for v in sheets['hph']['rows'][0]]
    sheets['hph']['name'], sheets['nm']['name'] = 'Patient Intake (MAIN)', 'NM Patient Log'
    sheets['hph']['hospital'], sheets['nm']['hospital'] = 'Humboldt Park', 'Northwestern'
    for s in sheets.values():
        s['letters'] = letters(len(s['header']))
        s['rowColors'] = row_colors(s)
    columns, names = [], set()
    for group, rows in d.GROUPS:
        for name, hph, nm, was, where, how, kind in rows:
            names.add(name)
            columns.append({'id': len(columns), 'group': group, 'name': name.replace('(new) ', ''), 'isNew': name.startswith('(new)'),
                            'hph': [x.strip() for x in hph.split(',') if x.strip()], 'nm': [x.strip() for x in nm.split(',') if x.strip()],
                            'was': was, 'where': where, 'how': how, 'kind': kind,
                            'steps': walk(TARGETS.get(name, []))})
    assert not set(TARGETS) - names, set(TARGETS) - names
    screens = {s for s, _, _ in SCREENS}
    assert all(t['screen'] in screens for c in columns for t in c['steps'])
    for s, _, _ in SCREENS:
        assert os.path.exists(os.path.join(HERE, 'img', s + '.jpg')), s
    data = {'sheets': sheets, 'columns': columns, 'screens': [{'id': s, 'title': t} for s, t, g in SCREENS]}
    with open(os.path.join(HERE, 'data.js'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.DATA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')
    print(len(columns), 'dictionary rows;', sum(1 for c in columns if c['steps']), 'with a walkthrough;', sum(len(c['steps']) for c in columns), 'steps;',
          len(SCREENS), 'screenshots')
    for name in ('MRN', 'Insurance / Responsible Payer', 'LTM/LVM', 'Added to Nimbly', 'Came Back to ER'):
        c = next(c for c in columns if c['name'] == name)
        print(' ', name, '->', ' | '.join(f"{s['kind']}:{s['screen']}" for s in c['steps']))
    print('row colours:', sheets['hph']['rowColors'], sheets['nm']['rowColors'])
    print('first fake patient:', [v for v in sheets['hph']['rows'][0][:20] if v != ''][:9])


if __name__ == '__main__':
    main()
